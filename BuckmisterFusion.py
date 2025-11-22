import adsk.core
import adsk.fusion
import math
import traceback

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Create command definition
        cmdDef = ui.commandDefinitions.addButtonDefinition(
            'BuckmisterFusionCmd',
            'Buckmister Fusion',
            'Creates a parametric geodesic sphere (Buckmister dome)',
            'resources'
        )

        # Add command created event handler
        onCommandCreated = CommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        handlers.append(onCommandCreated)

        # Add to CREATE panel in SOLID tab
        solidPanel = ui.allToolbarPanels.itemById('SolidCreatePanel')
        solidPanel.controls.addCommand(cmdDef)

    except:
        if ui:
            ui.messageBox('Failed:\\n{}'.format(traceback.format_exc()))

def stop(context):
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Clean up the UI
        cmdDef = ui.commandDefinitions.itemById('BuckmisterFusionCmd')
        if cmdDef:
            cmdDef.deleteMe()

        solidPanel = ui.allToolbarPanels.itemById('SolidCreatePanel')
        cntrl = solidPanel.controls.itemById('BuckmisterFusionCmd')
        if cntrl:
            cntrl.deleteMe()

    except:
        if ui:
            ui.messageBox('Failed:\\n{}'.format(traceback.format_exc()))

class CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            cmd = args.command
            inputs = cmd.commandInputs

            # Add inputs for sphere parameters
            inputs.addValueInput('radius', 'Radius', 'cm', 
                               adsk.core.ValueInput.createByReal(10.0))
            
            inputs.addIntegerSpinnerCommandInput('frequency', 'Frequency', 
                                               2, 6, 1, 3)

            # Option to create solid
            inputs.addBoolValueInput('createSolid', 'Create Solid Body', True, '', False)

            # Connect to the execute event
            onExecute = CommandExecuteHandler()
            cmd.execute.add(onExecute)
            handlers.append(onExecute)

        except:
            ui = adsk.core.Application.get().userInterface
            ui.messageBox('Failed:\\n{}'.format(traceback.format_exc()))

class CommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            app = adsk.core.Application.get()
            design = app.activeProduct
            
            # Get command inputs
            command = args.command
            inputs = command.commandInputs
            
            radius = inputs.itemById('radius').value
            frequency = inputs.itemById('frequency').value
            
            # Get create solid option
            createSolid = inputs.itemById('createSolid').value

            # Create geodesic sphere
            self.createGeodesicSphere(design, radius, frequency, createSolid)
            
        except:
            ui = adsk.core.Application.get().userInterface
            ui.messageBox('Failed:\\n{}'.format(traceback.format_exc()))

    def createGeodesicSphere(self, design, radius, frequency, createSolid):
        import os
        import sys
        lib_path = os.path.join(os.path.dirname(__file__), 'lib')
        if lib_path not in sys.path:
            sys.path.append(lib_path)
        from geodesic_math import GeodesicCalculator

        # Calculate geodesic points and faces
        calculator = GeodesicCalculator(radius, frequency)
        calculator.calculate()
        points = calculator.points
        faces = calculator.faces

        # Get root component
        app = adsk.core.Application.get()
        design = app.activeProduct
        root = design.rootComponent

        # Create new occurrence for the sphere
        occs = root.occurrences
        mat = adsk.core.Matrix3D.create()
        occ = occs.addNewComponent(mat)
        comp = occ.component

        if createSolid:
            # Create a solid body by making surfaces and stitching
            try:
                # Collect all surface bodies
                surface_bodies = []
                
                for face in faces:
                    v0 = points[face[0]]
                    v1 = points[face[1]]
                    v2 = points[face[2]]
                    
                    # Create temporary sketch for this face
                    temp_sketch = comp.sketches.add(comp.xYConstructionPlane)
                    
                    # Draw triangle
                    temp_sketch.sketchCurves.sketchLines.addByTwoPoints(v0, v1)
                    temp_sketch.sketchCurves.sketchLines.addByTwoPoints(v1, v2)
                    temp_sketch.sketchCurves.sketchLines.addByTwoPoints(v2, v0)
                    
                    # Get the profile (closed loop)
                    if temp_sketch.profiles.count > 0:
                        profile = temp_sketch.profiles.item(0)
                        
                        # Create a patch (surface) from this profile
                        patches = comp.features.patchFeatures
                        patchInput = patches.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                        patch = patches.add(patchInput)
                        
                        # Store the created surface body
                        if patch and patch.bodies.count > 0:
                            surface_bodies.append(patch.bodies.item(0))
                    
                    # Delete the sketch after creating the surface
                    temp_sketch.deleteMe()
                
                # Stitch all surfaces together to form a solid
                if len(surface_bodies) > 1:
                    stitchFeatures = comp.features.stitchFeatures
                    
                    # Create ObjectCollection with all surface bodies
                    bodiesToStitch = adsk.core.ObjectCollection.create()
                    for body in surface_bodies:
                        bodiesToStitch.add(body)
                    
                    # Create stitch input with tolerance
                    tolerance = adsk.core.ValueInput.createByReal(0.001)  # 0.001 cm tolerance
                    stitchInput = stitchFeatures.createInput(bodiesToStitch, tolerance)
                    
                    stitchFeatures.add(stitchInput)
                    
            except Exception as e:
                ui = adsk.core.Application.get().userInterface
                ui.messageBox('Failed to create solid:\n{}'.format(str(e)))
        else:
            # Create each face in a separate sketch (original behavior)
            sketches = comp.sketches
            for face in faces:
                v0 = points[face[0]]
                v1 = points[face[1]]
                v2 = points[face[2]]
                # Create a sketch on the XY plane (for simplicity)
                sk = sketches.add(comp.xYConstructionPlane)
                # Draw triangle
                sk.sketchCurves.sketchLines.addByTwoPoints(v0, v1)
                sk.sketchCurves.sketchLines.addByTwoPoints(v1, v2)
                sk.sketchCurves.sketchLines.addByTwoPoints(v2, v0)

handlers = []
