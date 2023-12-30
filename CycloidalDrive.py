#Author- Yang Li
#Description- Creates a cycloidal gear and base.

import adsk.core, adsk.fusion, adsk.cam, traceback
import math

def drange(start,stop,step):
    r=start
    while r<=stop:
        yield r
        r+=step

def cos(angle):
    return math.cos(math.radians(angle))

def sin(angle):
    return math.sin(math.radians(angle))

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        product=app.activeProduct
        design=adsk.fusion.Design.cast(product)
        rootComp=design.rootComponent
        sketches=rootComp.sketches
        extrudes=rootComp.features.extrudeFeatures
        xyPlane=rootComp.xYConstructionPlane
        sketch=sketches.add(xyPlane)

        #Design Parameters
        #Default units are in centimetres.
        pin_radius=0.25
        pin_circle_radius=5
        number_of_pins=10
        contraction=0.2
        thickness=0.5
        eccen=0.3
        centre_bearing_diameter=3
        transfer_holes=3

        rolling_circle_radius=pin_circle_radius/number_of_pins
        reduction_ratio=number_of_pins-1
        cycloid_base_radius=reduction_ratio*rolling_circle_radius

        #Creating the base of the drive.
        sketch=sketches.add(xyPlane)
        circles=[]
        #The pins.
        for pin in range(number_of_pins):
            angle=pin*360/number_of_pins
            circles.append(sketch.sketchCurves.sketchCircles.addByCenterRadius(
                adsk.core.Point3D.create(eccen+cos(angle)*pin_circle_radius,
                                         sin(angle)*pin_circle_radius,0),
                                         pin_radius))
        for pin in range(number_of_pins):
            profile=sketch.profiles.item(pin)
            distance=adsk.core.ValueInput.createByReal(thickness)
            extrude1=extrudes.addSimple(profile,distance,adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        #The main base.
        sketch=sketches.add(xyPlane)
        circles=[]
        circles.append(sketch.sketchCurves.sketchCircles.addByCenterRadius(
                adsk.core.Point3D.create(eccen,0,0),
                                         pin_circle_radius+pin_radius*2))
        circles.append(sketch.sketchCurves.sketchCircles.addByCenterRadius(
                adsk.core.Point3D.create(eccen,0,0),
                                         eccen*5))
        profile=sketch.profiles.item(0)
        distance=adsk.core.ValueInput.createByReal(-thickness)
        extrude1=extrudes.addSimple(profile,distance,adsk.fusion.FeatureOperations.JoinFeatureOperation)

        #Creating cycloidal gear.
        sketch=sketches.add(xyPlane)
        points=adsk.core.ObjectCollection.create()
        for angle in drange(0,360,5):
            x=(cycloid_base_radius+rolling_circle_radius)*cos(angle)
            y=(cycloid_base_radius+rolling_circle_radius)*sin(angle)
            point_x=x+(rolling_circle_radius-contraction)*cos(number_of_pins*angle)
            point_y=y+(rolling_circle_radius-contraction)*sin(number_of_pins*angle)
            points.add(adsk.core.Point3D.create(point_x,point_y,0))
        temp_cycloid_gear=sketch.sketchCurves.sketchFittedSplines.add(points)
        direction_point=adsk.core.Point3D.create(0,0,0)
        cycloid_gear=sketch.offset(sketch.findConnectedCurves(temp_cycloid_gear),direction_point,pin_radius)
        temp_cycloid_gear.deleteMe()
        sketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0,0,0),centre_bearing_diameter/2)
        for hole in range(transfer_holes):
            angle=hole*360/transfer_holes
            sketch.sketchCurves.sketchCircles.addByCenterRadius(
                adsk.core.Point3D.create(cos(angle)*centre_bearing_diameter,
                                         sin(angle)*centre_bearing_diameter,0),
                                         pin_radius+eccen)
        profile=sketch.profiles.item(0)
        distance=adsk.core.ValueInput.createByReal(thickness)
        extrude1=extrudes.addSimple(profile,distance,adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
