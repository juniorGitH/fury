import numpy as np
from fury import window, actor, ui, utils
import itertools
import pybullet as p

# Instantiate Pybullet client.
client = p.connect(p.GUI)
# Apply gravity to the scene.
p.setGravity(0, 0, -10, physicsClientId=client)

###### Creating ceiling Plane
ceil_actor = actor.box(centers=np.array([[0, 0, 0]]),
                         directions=[0,0,0],
                         size=(5, 5, 0.2) ,
                         colors=(255, 255, 255))
ceil_coll = p.createCollisionShape(p.GEOM_BOX,
                                   halfExtents=[2.5, 2.5, 0.1]) # half of the actual size.
ceil = p.createMultiBody(baseMass=0,
                          baseCollisionShapeIndex=ceil_coll,
                          basePosition=[0, 0, -0.2],
                          baseOrientation=[ 0, 0, 0, 1 ])

def sync_actor(actor, multibody):
    pos, orn = p.getBasePositionAndOrientation(multibody)
    actor.SetPosition(*pos)
    orn_deg = np.degrees(p.getEulerFromQuaternion(orn))
    actor.SetOrientation(*orn_deg)
    # actor.RotateWXYZ(*orn)

############ Creating String
sphereRadius = 0.25
segment_size = (0.1, 0.1, 0.25)
###### Creating BALL
# Ball actor
ball_actor = actor.sphere(centers = [[0, 0, 0]],
                    colors=np.array([1,0,0]),
                    radii=0.25)

# Creating a Multibody which will be tracked by pybullet.
useMaximalCoordinates = False
# colBoxId = p.createCollisionShapeArray([p.GEOM_BOX, p.GEOM_SPHERE],radii=[sphereRadius+0.03,sphereRadius+0.03], halfExtents=[[sphereRadius,sphereRadius,sphereRadius],[sphereRadius,sphereRadius,sphereRadius]])
sphere = p.createCollisionShape(p.GEOM_SPHERE,
                                  radius=sphereRadius)
colBoxId = p.createCollisionShape(p.GEOM_BOX,
                                  halfExtents=segment_size)

pendulum_actors = []

mass = 1
visualShapeId = -1

link_Masses = np.zeros(7)
link_Masses[:] = 0.5

linkCollisionShapeIndices = np.zeros(7)
linkCollisionShapeIndices[:] = np.array(colBoxId)
linkVisualShapeIndices = -1 * np.ones(7)
linkPositions = np.zeros((7, 3))
linkPositions[:] = np.array([0, 0, segment_size[2] * 2.0 + 0.01])
linkOrientations = np.zeros((7, 4))
linkOrientations[:] = np.array([0, 0, 0, 1])
linkInertialFramePositions = np.zeros((7, 3))
linkInertialFrameOrientations = np.zeros((7, 4))
linkInertialFrameOrientations[:] = np.array([0, 0, 0, 1])
indices = np.arange(7)
jointTypes = np.zeros(7)
jointTypes[:] = np.array(p.JOINT_SPHERICAL)
axis = np.zeros((7, 3))
axis[:] = np.array([0, 0, 1])

linkDirections = np.zeros((7, 3))
linkDirections[:] = np.array([1.57, 0, 0])

linkSizes = np.zeros((7, 3))
linkSizes[:] = np.array(segment_size)*2

segment_actor = actor.box(centers=linkPositions,
                          directions=linkDirections,
                          colors=np.random.rand(7, 3)*255,
                          scale=linkSizes)

# print(link_Masses.shape)
# print(linkCollisionShapeIndices.shape)
# print(linkVisualShapeIndices.shape)
# print(linkPositions.shape)
# print(linkOrientations.shape)
# print(linkInertialFrameOrientations.shape)
# print(linkInertialFramePositions.shape)
# print(indices.shape)
# print(jointTypes.shape)
# print(axis.shape)
# print()

basePosition = [0, 0, 1]
baseOrientation = [0, 0, 0, 1]
pendulum = p.createMultiBody(mass,
                              sphere,
                              visualShapeId,
                              basePosition,
                              baseOrientation,
                              linkMasses=link_Masses,
                              linkCollisionShapeIndices=linkCollisionShapeIndices,
                              linkVisualShapeIndices=linkVisualShapeIndices,
                              linkPositions=linkPositions,
                              linkOrientations=linkOrientations,
                              linkInertialFramePositions=linkInertialFramePositions,
                              linkInertialFrameOrientations=linkInertialFrameOrientations,
                              linkParentIndices=indices,
                              linkJointTypes=jointTypes,
                              linkJointAxis=axis)
                            #   useMaximalCoordinates=useMaximalCoordinates)

scene = window.Scene()
scene.add(actor.axes())
scene.add(segment_actor)
scene.add(ball_actor)
scene.add(ceil_actor)



# Create show manager.
showm = window.ShowManager(scene,
                           size=(900, 768), reset_camera=False,
                           order_transparent=True)

showm.initialize()

# Counter interator for tracking simulation steps.
counter = itertools.count()

# Function for syncing actors with multibodies.
def sync_actor(actor, multibody):
    pos, orn = p.getBasePositionAndOrientation(multibody)
    actor.SetPosition(*pos)
    orn_deg = np.degrees(p.getEulerFromQuaternion(orn))
    actor.SetOrientation(*orn_deg)
    # actor.RotateWXYZ(*orn)

sync_actor(ceil_actor, ceil)

# print(pendulum_actors)
# for joint in range(p.getNumJoints(pendulum)):
#     print(p.getJointInfo(pendulum, joint))

vertices = utils.vertices_from_actor(segment_actor)
num_vertices = vertices.shape[0]
num_objects = linkPositions.shape[0]
sec = np.int(num_vertices / num_objects)

def sync_joints(actor_list, multibody):
    for joint in range(p.getNumJoints(multibody)):
        pos, orn = p.getLinkState(multibody, joint)[4:6]

        rot_mat = np.reshape(
            p.getMatrixFromQuaternion(
                p.getDifferenceQuaternion(orn, linkOrientations[joint])),
            (3, 3))

        vertices[joint * sec: joint * sec + sec] = \
            (vertices[joint * sec: joint * sec + sec] -
            linkPositions[joint])@rot_mat + pos

        linkPositions[joint] = pos
        linkOrientations[joint] = orn

def timer_callback(_obj, _event):
    cnt = next(counter)
    showm.render()

    # Set position and orientation of the ball.
    # sync_actor(ceil_actor, ceil)
    for i in range(p.getNumJoints(pendulum)):
        sync_actor(ball_actor, sphere)
        sync_joints(pendulum_actors, pendulum)
        utils.update_actor(segment_actor)

    # Simulate a step.
    p.stepSimulation()

    # Exit after 2000 steps of simulation.
    # if cnt == 2000:
    #     showm.exit()

# Add the timer callback to showmanager.
# Increasing the duration value will slow down the simulation.
showm.add_timer_callback(True, 1, timer_callback)

interactive = True

# start simulation
if interactive: showm.start()
