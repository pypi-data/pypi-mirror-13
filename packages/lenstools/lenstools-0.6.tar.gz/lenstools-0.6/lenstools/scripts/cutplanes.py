#######################################################################
################Cut lens planes out of a Gadget2 snapshot##############
#######################################################################

from __future__ import division

import sys,os
import json

from lenstools.simulations.logs import logdriver,logstderr,peakMemory,peakMemoryAll

from lenstools.pipeline.simulation import SimulationBatch
from lenstools.pipeline.settings import PlaneSettings
from lenstools.simulations import DensityPlane,PotentialPlane

from lenstools.utils import MPIWhirlPool
from lenstools import configuration

import numpy as np

#FFT engine
fftengine = configuration.fftengine()

#######################################################
################Main execution#########################
#######################################################


def main(pool,batch,settings,id,override):

	#Safety check
	assert isinstance(pool,MPIWhirlPool) or (pool is None)
	assert isinstance(batch,SimulationBatch)
	assert isinstance(settings,PlaneSettings)

	#Split the id into the model,collection and realization parts
	cosmo_id,geometry_id,realization_id = id.split("|")

	#Get a handle on the simulation model
	model = batch.getModel(cosmo_id)

	#Scale the box size to the correct units
	nside,box_size = geometry_id.split("b")
	box_size = float(box_size)*model.Mpc_over_h

	#Get the realization number
	ic = int(realization_id.strip("ic"))

	#Instantiate the appropriate SimulationIC object
	realization = model.getCollection(box_size,nside).getRealization(ic)
	snapshot_path = realization.snapshot_subdir
	
	#Base name of the snapshot files
	SnapshotFileBase = realization.SnapshotFileBase

	#Log to user
	if (pool is None) or (pool.is_master()):
		logdriver.info("Fast Fourier Transform operations handler: {0}".format(fftengine.__class__.__name__))
		logdriver.info("Reading snapshots from {0}".format(os.path.join(snapshot_path,SnapshotFileBase+"*")))

	#Construct also the SimulationPlanes instance, to handle the current plane batch
	plane_batch = realization.getPlaneSet(settings.directory_name)
	save_path = plane_batch.storage_subdir

	#Override settings from the command line
	if override is not None:
		
		override_dict = json.loads(override)
		for key in override_dict.keys():

			if not hasattr(settings,key):
				raise AttributeError("Plane settings have no such attribute: '{0}'".format(key))

			if (pool is None) or (pool.is_master()):
				logdriver.info("Overriding original setting {0}={1} with command line value {0}={2}".format(key,getattr(settings,key),override_dict[key]))

			setattr(settings,key,override_dict[key])


	#Override with pickled options in storage subdir if prompted by user
	if settings.override_with_local:
		
		local_settings_file = os.path.join(plane_batch.home,"settings.p")
		settings = PlaneSettings.read(local_settings_file)
		assert isinstance(settings,PlaneSettings)

		if (pool is None) or (pool.is_master()):
			logdriver.warning("Overriding settings with the previously pickled ones at {0}".format(local_settings_file))


	if (pool is None) or (pool.is_master()):
		
		logdriver.info("Planes will be saved to {0}".format(save_path))
		#Open the info file to save the planes information
		infofile = open(plane_batch.path("info.txt"),"w")

	#Read from PlaneSettings
	plane_resolution = settings.plane_resolution
	
	first_snapshot = settings.first_snapshot
	last_snapshot = settings.last_snapshot
	if first_snapshot is None:
		snapshots = settings.snapshots
	else:
		snapshots = range(first_snapshot,last_snapshot+1)
	
	cut_points = settings.cut_points
	normals = settings.normals
	thickness = settings.thickness
	thickness_resolution = settings.thickness_resolution
	smooth = settings.smooth
	kind = settings.kind

	#Place holder for the lensing density on the plane
	density_projected = np.empty((plane_resolution,)*2,dtype=np.float32)

	#Open a RMA window on the density placeholder
	if pool is not None:
		pool.openWindow(density_projected)
		
		if pool.is_master():
			logdriver.debug("Opened density window of type {0}".format(pool._window_type))

	#Pre--compute multipoles for solving Poisson equation
	lx,ly = np.meshgrid(fftengine.fftfreq(plane_resolution),fftengine.rfftfreq(plane_resolution),indexing="ij")
	l_squared = lx**2 + ly**2
				
	#Avoid dividing by 0
	l_squared[0,0] = 1.0

	#Arguments
	kwargs = {

	"plane_resolution" : plane_resolution,
	"thickness_resolution" : thickness_resolution,
	"smooth" : smooth,
	"kind" : kind,
	"density_placeholder" : density_projected,
	"l_squared" : l_squared

	}

	#Log the initial memory load
	peak_memory_task,peak_memory_all = peakMemory(),peakMemoryAll(pool)
	if (pool is None) or (pool.is_master()):
		logstderr.info("Initial memory usage: {0:.3f} (task), {1[0]:.3f} (all {1[1]} tasks)".format(peak_memory_task,peak_memory_all))


	num_planes_total = len(snapshots)*len(cut_points)*len(normals)
	nplane = 1 

	#Cycle over each snapshot
	for n in snapshots:

		#Log
		if (pool is None) or (pool.is_master()):
			logdriver.info("Waiting for input files from snapshot {0}...".format(n))
		
		#Open the snapshot
		snapshot_filename = realization.path(configuration.snapshot_handler.int2root(SnapshotFileBase,n),where="snapshot_subdir")
		if pool is not None:
			logdriver.info("Task {0} reading nbody snapshot from {1}".format(pool.comm.rank,snapshot_filename))

		snap = configuration.snapshot_handler.open(snapshot_filename,pool=pool)

		if pool is not None:
			logdriver.debug("Task {0} read nbody snapshot from {1}".format(pool.comm.rank,snapshot_filename))

		#Get the positions of the particles
		if not hasattr(snap,"positions"):
			snap.getPositions()

		#Log memory usage
		if (pool is None) or (pool.is_master()):
			logstderr.debug("Read particle positions: peak memory usage {0:.3f} (task)".format(peakMemory()))

		#Close the snapshot file
		snap.fp.close()

		#Update the summary info file
		if (pool is None) or (pool.is_master()):
			infofile.write("s={0},d={1},z={2}\n".format(n,snap.header["comoving_distance"],snap.header["redshift"]))

		#Cut the lens planes
		for cut,pos in enumerate(cut_points):
			for normal in normals:

				if pool is None or pool.is_master():
					logdriver.info("Cutting {0} plane at {1} with normal {2},thickness {3}, of size {4} x {4}".format(kind,pos,normal,thickness,snap.header["box_size"]))

				############################
				#####Do the cutting#########
				############################
				
				plane,resolution,NumPart = snap.cutPlaneGaussianGrid(normal=normal,center=pos,thickness=thickness,left_corner=np.zeros(3)*snap.Mpc_over_h,**kwargs)
				
				#######################################################################################################################################

				#Save the plane
				plane_file = batch.syshandler.map(os.path.join(save_path,settings.name_format.format(n,kind,cut,normal,settings.format)))

				if (pool is None) or (pool.is_master()):
			
					#Wrap the plane in a PotentialPlane object
					if kind=="potential":
						plane_wrap = PotentialPlane(plane.value,angle=snap.header["box_size"],redshift=snap.header["redshift"],comoving_distance=snap.header["comoving_distance"],cosmology=snap.cosmology,num_particles=NumPart,unit=plane.unit)
					elif kind=="density":
						plane_wrap = DensityPlane(plane,angle=snap.header["box_size"],redshift=snap.header["redshift"],comoving_distance=snap.header["comoving_distance"],cosmology=snap.cosmology,num_particles=NumPart)
					else:
						raise NotImplementedError("Plane of kind '{0}' not implemented!".format(kind))

					#Save the result
					logdriver.info("Saving plane to {0}".format(plane_file))
					plane_wrap.save(plane_file)
					logdriver.debug("Saved plane to {0}".format(plane_file))


				#Log peak memory usage
				peak_memory_task,peak_memory_all = peakMemory(),peakMemoryAll(pool)
				if (pool is None) or (pool.is_master()):
					logstderr.info("Plane {0} of {1} completed, peak memory usage: {2:.3f} (task), {3[0]:.3f} (all {3[1]} tasks)".format(nplane,num_planes_total,peak_memory_task,peak_memory_all))

				nplane += 1
			
				#Safety barrier sync
				if pool is not None:
					pool.comm.Barrier()


		#Close the snapshot
		snap.close()

	#Safety barrier sync
	if pool is not None:
		pool.comm.Barrier()

		#Close the RMA window
		pool.closeWindow()
		
		if pool.is_master():
			logdriver.debug("Closed density window of type {0}".format(pool._window_type))

	#Close the infofile
	if (pool is None) or (pool.is_master()):
		infofile.close()

	if pool is None or pool.is_master():
		logdriver.info("DONE!!")
