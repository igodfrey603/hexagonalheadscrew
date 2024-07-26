# screw_handler.py

import adsk.core, adsk.fusion, adsk.cam, traceback
import os
import math
from math import cos, sin, radians, pi
import importlib.util
import sys



_handlers = []


_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)
_units = ''
app = adsk.core.Application.get()
_ui = app.userInterface


# Define the file path to your script
file_path = '/path/to/config.py'
file1 =  os.path.expanduser('~AppData/Roaming/Autodesk/ApplicationPlugins/DINFASTENERS.bundle/Contents/config.py')
file2 =  os.path.expanduser('~AppData/Roaming/Autodesk/ApplicationPlugins/DINFASTENERS.bundle/Contents/lib/fusion360utils"')


# Create a module spec from the file path
spec = importlib.util.spec_from_file_location("config", file1)

# Create a new module based on the spec
config = importlib.util.module_from_spec(spec)

# Load the module
spec.loader.exec_module(config)

# Create a module spec from the file path
spec = importlib.util.spec_from_file_location("fusion360utils", file2)

# Create a new module based on the spec
fusion360utils = importlib.util.module_from_spec(spec)

# Load the module
spec.loader.exec_module(fusion360utils)
module = importlib.util.module_from_spec(spec)
sys.modules[futil] = module

# Now you can use the module with the alias
import futil

# Now you can use the module

def getCommandInputValue(commandInput, unitType):
    try:
        valCommandInput = adsk.core.ValueCommandInput.cast(commandInput)
        if not valCommandInput:
            return (False, 0)

        # Verify that the expression is valid.
        des = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct)
        unitsMgr = des.unitsManager
        
        if unitsMgr.isValidExpression(valCommandInput.expression, unitType):
            value = unitsMgr.evaluateExpression(valCommandInput.expression, unitType)
            return (True, value)
        else:
            return (False, 0)
    except:
        ui = adsk.core.Application.get().userInterface
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def command_created(args: adsk.core.CommandCreatedEventArgs):
    futil.log(f'{config.ADDIN_NAME} Command Created Event')
    
    inputs = args.command.commandInputs
    futil.log(f'{config.ADDIN_NAME} Command Created Event')

    eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
    des = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct)
    if not des:
        adsk.core.Application.get().userInterface.messageBox('A Fusion design must be active when invoking this command.')
        return()
        
    defaultUnits = des.unitsManager.defaultLengthUnits
    global _units
    if defaultUnits == 'in' or defaultUnits == 'ft':
        _units = 'in'
    else:
        _units = 'mm'

    diameter = 'M10'
    diameterAttrib = des.attributes.itemByName('Socketheadscrew', 'diameter')
    if diameterAttrib:
        diameter = diameterAttrib.value

    length = '10'
    lengthAttrib = des.attributes.itemByName('Socketheadscrew', 'length')
    if lengthAttrib:
        length = lengthAttrib.value

    lengthcustom = 10
    lengthcustomAttrib = des.attributes.itemByName('Socketheadscrew', 'lengthcustom')
    if lengthcustomAttrib:
        lengthcustom = float(lengthcustomAttrib.value)    

    threadlenght = 10
    threadlengthAttrib = des.attributes.itemByName('Socketheadscrew', 'threadlength')
    if threadlengthAttrib:
        threadlenght = threadlengthAttrib.value      

    cmd = eventArgs.command
    cmd.isExecutedWhenPreEmpted = False
    inputs = cmd.commandInputs
    global _length, _lengthcustom, _diameter, _threadlenght, selObj

    imagePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', 'SocketheadscrewEnglish.png')
    _imgInputEnglish = inputs.addImageCommandInput('socketheadscrewImageEnglish', '', imagePath)
    _imgInputEnglish.isFullWidth = True

    _diameter = inputs.addDropDownCommandInput('diameter', 'Diameter', adsk.core.DropDownStyles.TextListDropDownStyle)
    if diameter == 'M1.6':
        _diameter.listItems.add('M1.6', True)
    else:
        _diameter.listItems.add('M1.6', False)

    _length = inputs.addDropDownCommandInput('length', 'Length', adsk.core.DropDownStyles.TextListDropDownStyle)
    if length == '2':
        _length.listItems.add('2', True)
    else:
        _length.listItems.add('2', False)

    sel = adsk.core.Application.get().userInterface.selectEntity('Select a point to create hexagon head screw', 'Edges,SketchCurves')
    selObj = sel.entity 

    onExecute = SocketheadscrewCommandExecuteHandler()
    cmd.execute.add(onExecute)
    _handlers.append(onExecute)

class SocketheadscrewCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)
            des = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct)
            attribs = des.attributes
            attribs.add('Socketheadscrew', 'length', _length.selectedItem.name)
            attribs.add('Socketheadscrew', 'diameter', _diameter.selectedItem.name)

            if _diameter.selectedItem.name == 'M1.6':
                diameter = 0.16 / 2

            if _length.selectedItem.name == '2':
                length = 0.2

            filletradius = (diameter * 0.2)
            headlength = None 
            if _diameter.selectedItem.name == 'M1.6':
                headlength = 1.22 / 10

            tophead = length + (2 * diameter)
            headdistance = (headlength)
            hexdistance = (-1 * (diameter))
            chamferlength = (diameter * 2 * 0.075)

            keysize = None 
            if _diameter.selectedItem.name == 'M1.4':
                keysize = 0.13 / 1.73

            SocketheadscrewComp = drawSocketheadscrew( des, length,  tophead, diameter, headlength, headdistance, hexdistance, chamferlength, keysize, filletradius, selObj)

           
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Builds a SOCKET HEAD SCREW.
def drawSocketheadscrew(design, length,  tophead, diameter,  headlength, headdistance, hexdistance, chamferlength, keysize, filletradius, selObj):
    try:                
    

        
        # create a new component
        diameter_name = str((diameter*2)*10)
        length_name = str(length*10)
        rootComp = design.rootComponent
        allOccs = rootComp.occurrences
        newOcc = allOccs.addNewComponent(adsk.core.Matrix3D.create())
        newComponent = newOcc.component
        newComponent.name = "hexagonalheadscrew "+'M'+diameter_name+','+length_name



        

        
        extrudes = newComponent.features.extrudeFeatures
        constructionPlanes = rootComp.constructionPlanes
        filletFeats = newComponent.features.filletFeatures
        chamferFeats = newComponent.features.chamferFeatures
        loft_features = newComponent.features.loftFeatures

        # create a new sketch
        sketches = newComponent.sketches
        sketch1 = sketches.add(rootComp.xZConstructionPlane)

        # Create sketch lines
        circles = sketch1.sketchCurves.sketchCircles

        # Create some 3D points
        circle1 = circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), diameter)

        # Create an extrusion
        prof = sketch1.profiles.item(0)
        distance = adsk.core.ValueInput.createByReal(length)
        extrude1 = extrudes.addSimple(prof, distance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        body1 = extrude1.bodies.item(0)
        body1.name = "shank"

        # create an offset plane
        planeInput = constructionPlanes.createInput()
        planeInput.setByOffset(rootComp.xZConstructionPlane, adsk.core.ValueInput.createByReal(length))
        offsetPlane = constructionPlanes.add(planeInput)

        

      

        # create the hexagon
        sketches = newComponent.sketches
        sketch3 = sketches.add(offsetPlane)

        # Define the parameters for the hexagon
        center = adsk.core.Point3D.create(0, 0, 0)
        radius = keysize  
        numSides = 6  # Hexagon has 6 sides

        # Calculate the angle between sides
        angle = 360.0 / numSides

        # Create the hexagon
        lines = sketch3.sketchCurves.sketchLines
        for i in range(numSides):
            startAngle = i * angle
            endAngle = (i + 1) * angle
            startPoint = adsk.core.Point3D.create(
                center.x + radius * cos(radians(startAngle)),
                center.y + radius * sin(radians(startAngle)),
                center.z
            )
            endPoint = adsk.core.Point3D.create(
                center.x + radius * cos(radians(endAngle)),
                center.y + radius * sin(radians(endAngle)),
                center.z
            )
            lines.addByTwoPoints(startPoint, endPoint)

        # create the third extrusion
        prof = sketch3.profiles.item(0)
        distance = adsk.core.ValueInput.createByReal(-hexdistance)
        extrude3 = extrudes.addSimple(prof, distance, adsk.fusion.FeatureOperations.JoinFeatureOperation)
        body1 = extrude3.bodies.item(0)
        # get edges to fillet
        edgeCol = adsk.core.ObjectCollection.create()
        loops = extrude1.sideFaces[0].loops
        edgeLoop = None
        for edgeLoop in loops:
            if (len(edgeLoop.edges) == 1):
                break
        # create a fillet
        edgeCol.add(edgeLoop.edges[0])
        filletInput = filletFeats.createInput()
        filletSize = adsk.core.ValueInput.createByReal(filletradius)
        filletInput.addConstantRadiusEdgeSet(edgeCol, filletSize, True)
        filletFeats.add(filletInput)

       
        sideFace = extrude1.sideFaces[0]
        threads = newComponent.features.threadFeatures
        threadDataQuery = threads.threadDataQuery
        defaultThreadType = threadDataQuery.defaultMetricThreadType
        recommendData = threadDataQuery.recommendThreadData(diameter*2, False, defaultThreadType)
        if recommendData[0] :
            threadInfo = threads.createThreadInfo(False, defaultThreadType, recommendData[1], recommendData[2])
            faces = adsk.core.ObjectCollection.create()
            faces.add(sideFace)
            threadInput = threads.createInput(faces, threadInfo)
            threads.add(threadInput)

        



        # get edges to chamfer
        faces = extrude1.faces
        body = faces[0].body
        edges = extrude1.startFaces[0].edges
        edgeCol = adsk.core.ObjectCollection.create()
        for edge in edges:
            edgeCol.add(edge)
        # create chamfer
        chamferInput = chamferFeats.createInput(edgeCol, True)
        chamferInput.isSymmetric = False
        chamferInput.setToEqualDistance(adsk.core.ValueInput.createByReal(chamferlength))
        chamferFeats.add(chamferInput)
        # create an offset plane 
       

        


        # Create the first joint geometry with the end face
        geo0 = adsk.fusion.JointGeometry.createByCurve(circle1, adsk.fusion.JointKeyPointTypes.CenterKeyPoint)
        # Create the second joint geometry with the sketch line
        geo1 = adsk.fusion.JointGeometry.createByCurve(selObj, adsk.fusion.JointKeyPointTypes.CenterKeyPoint)
         
        # Create joint input
        joints = rootComp.joints
        jointInput = joints.createInput(geo0, geo1)

        # Set the joint input
        angle = adsk.core.ValueInput.createByString('90 deg')
        offset = adsk.core.ValueInput.createByReal(length+headlength)
        jointInput.angle = angle
        jointInput.offset = offset
        jointInput.isFlipped = True
        jointInput.setAsRigidJointMotion
        
        # Create the joint
        joint = joints.add(jointInput)

        # Group everything used to create the gear in the timeline.
        timelineGroups = design.timeline.timelineGroups
        newOccIndex = newOcc.timelineObject.index
        screwIndex = extrude3.timelineObject.index
        timelineGroup = timelineGroups.add(newOccIndex, screwIndex)
        timelineGroup.name = 'screw'



        
       

       

        design.activateRootComponent()
     

    



       


    except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))   
