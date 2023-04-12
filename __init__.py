bl_info = {
    "name" : "The TF2 Trifecta",
    "description" : "A group of three addons: Wardrobe, Merc Deployer, and Bonemerge.",
    "author" : "hisanimations",
    "version" : (2, 0, 2),
    "blender" : (3, 5, 0),
    "location" : "View3d > Wardrobe, View3d > Merc Deployer, View3d > Bonemerge",
    "support" : "COMMUNITY",
    "category" : "Porting",
    "doc_url": "https://github.com/hisprofile/TF2-Trifecta/blob/main/README.md"
}

import bpy, json, os
from pathlib import Path
from bpy.props import *
from bpy.types import *
from mathutils import *
from bpy.app.handlers import persistent
from datetime import datetime
import importlib, sys
for filename in [f for f in os.listdir(os.path.dirname(os.path.realpath(__file__))) if f.endswith(".py") ]:
    if filename == os.path.basename(__file__): continue
    module = sys.modules.get("{}.{}".format(__name__,filename[:-3]))
    if module: importlib.reload(module)
from bpy.app.handlers import persistent
# borrowed from BST
from . import bonemerge, mercdeployer, icons, updater, newuilist, preferences
global addn
addn = "Wardrobe" # addon name
classes = []

def RemoveNodeGroups(a): # iterate through every node and node group by using the "tree" method and removing said nodes
    for i in a.nodes:
        if i.type == 'GROUP':
            RemoveNodeGroups(i.node_tree)
            i.node_tree.user_clear()
            a.nodes.remove(i)
        else:
            a.nodes.remove(i)

def returnsearch(a):
    path = str(Path(__file__).parent)
    path = path + "/master.json"
    if not bpy.context.scene.hisanimvars.hisanimweapons:
        files = ["scout", "soldier", "pyro", "demo", "heavy", "engineer", "sniper", "medic", "spy", "allclass", "allclass2", "allclass3"]
    else:
        files = ['weapons']
    cln = ["named", "unnamed"]
    f = open(path)
    cosmetics = json.loads(f.read())
    f.close()
    hits = []
    for key in a:
        for i in files:
            for ii in cln:
                for v in cosmetics[i][ii]:
                    if key.casefold() in v.casefold() and not f'{v}_-_{i}' in hits:
                        hits.append(f'{v}_-_{i}')
                    
    return hits

def ReuseImage(a, path):
    if bpy.context.scene.hisanimvars.savespace:
        bak = a.image.name
        a.image.name = a.image.name.upper()
        link(path, bak, 'Image') # link an image

        if (newimg := bpy.data.images.get(bak)) != None: # if the linked image was truly linked, replace the old image with the linked image and stop the function.
            a.image = newimg
            return None
        # if the function was not stopped, then revert the image name
        del newimg
        a.image.name = bak
    if ".0" in a.image.name: # if .0 is in the name, then it is most likely a duplicate. it will try to search for the original. and use that instead.
        lookfor = a.image.name[:a.image.name.rindex(".")]
        print(f'looking for {lookfor}...')
        if (lookfor := bpy.data.images.get(lookfor)) != None:
            a.image = lookfor
            print("found!")
            a.image.use_fake_user = False
            return None
        else: # the image is the first despite it having .0 in its name, then rename it.
            del lookfor
            print(f"no original match found for {a.image.name}! Renaming...")
            old = a.image.name
            new = a.image.name[:a.image.name.rindex(".")]
            print(f'{old} --> {new}')
            a.image.name = new
            a.image.use_fake_user = False
            return None
    print(f'No match for {a.image.name}! How odd...')
    return

def Collapse(a, b): # merge TF2 BVLG groups
    if a.type == 'GROUP' and b in a.node_tree.name:
        c = b + "-WDRB"
        if a.node_tree.name == c:
            return "continue"
        if bpy.data.node_groups.get(c) != None:
            RemoveNodeGroups(a.node_tree)
            a.node_tree = bpy.data.node_groups[c]
        else:
            a.node_tree.name = c
            mercdeployer.NoUserNodeGroup(a.node_tree)

def link(a, b, c): # get a class from TF2-V3
    blendfile = a
    section = f"/{c}/"
    object = b
    
    directory = blendfile + section
    
    bpy.ops.wm.link(filename=object, directory=directory)


@persistent
def updatefaces(scn):
    print('f')
    props = bpy.context.scene.hisanimvars
    try:
        data = bpy.context.object.data
    except:
        return None
    if data.get('aaa_fs') == None: return None
    props.activeface = bpy.context.object

    if props.activeface != props.lastactiveface:
        props.sliders.clear()
        for i in data.keys():
            try:
                data.id_properties_ui(i)
                if props.lockfilter not in i: raise
            except:
                continue
            new = props.sliders.add()
            new.name = i
    props.lastactiveface = props.activeface

class HISANIM_UL_SLIDERS(bpy.types.UIList):

    def draw_item(self, context,
            layout, data,
            item, icon,
            active_data, active_propname,
            index):
        props = context.scene.hisanimvars
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            #layout.prop(props.activeface.data, f'["{item.name}"]')
            layout.label(text=item.name)
            layout.prop(item, 'value')

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text='')

class HISANIM_OT_AddLightwarps(bpy.types.Operator): # switch to lightwarps with a button
    bl_idname = 'hisanim.lightwarps'
    bl_label = 'Use Lightwarps (TF2 Style)'
    bl_description = 'Make use of the lightwarps to achieve a better TF2 look'
    bl_options = {'UNDO'}
    
    def execute(self, context):
        if (NT := bpy.data.node_groups.get('VertexLitGeneric-WDRB')) == None: 
            self.report({'INFO'}, 'Cosmetic and class needed to proceed!')
            return {'CANCELLED'}
        
        NT.nodes['Group'].node_tree.use_fake_user = True
        NT.nodes['Group'].node_tree = bpy.data.node_groups['tf2combined-eevee']
        if NT.nodes.get('Lightwarp') == None:
            NT.nodes.new(type="ShaderNodeTexImage").name = "Lightwarp"
        if (IMG := bpy.data.images.get('pyro_lightwarp.png')) == None:
            for i in range(100):
                num = f'{"0"*(3-len(str(i)))}{str(i)}'
                if (IMG := bpy.data.images.get(f'pyro_lightwarp.png.{num}')) != None:
                    NT.nodes['Lightwarp'].image = IMG
                    break
            else:
                self.report({'INFO'}, 'Add a class first!')
                return {'CANCELLED'}
        else:
            NT.nodes['Lightwarp'].image = IMG
        
        NT.nodes['Lightwarp'].location[0] = 960
        NT.nodes['Lightwarp'].location[1] = -440
        NT.links.new(NT.nodes['Group'].outputs['lightwarp vector'], NT.nodes['Lightwarp'].inputs['Vector'])
        NT.links.new(NT.nodes['Lightwarp'].outputs['Color'], NT.nodes['Group'].inputs['Lightwarp'])
        return {'FINISHED'}

class HISANIM_OT_RemoveLightwarps(bpy.types.Operator): # be cycles compatible
    bl_idname = 'hisanim.removelightwarps'
    bl_label = 'Make Cycles compatible (Default)'
    bl_description = 'Make the cosmetics Cycles compatible'
    bl_options = {'UNDO'}
    
    def execute(self, execute):
        if (NT := bpy.data.node_groups.get('VertexLitGeneric-WDRB')) == None:
            self.report({'INFO'}, 'Cosmetic needed to proceed!')
            return {'CANCELLED'}
        NT.nodes['Group'].node_tree = bpy.data.node_groups['tf2combined-cycles']
        return {'FINISHED'}
        
class searchHits(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()

class HISANIM_OT_SLIDERESET(bpy.types.Operator):
    bl_idname = 'hisanim.resetslider'
    bl_label = ''
    slider = bpy.props.StringProperty()
    stop: bpy.props.BoolProperty()
    
    def modal(self, context, event):
        props = bpy.context.scene.hisanimvars
        self.slider = props.activeslider
        if self.stop:
            props.dragging = False
            props.sliders[self.slider].value = 0
            return {'FINISHED'}
        if event.value == 'RELEASED':
            self.stop = True
        return {'PASS_THROUGH'}
    def invoke(self, context, event):
        self.stop = False
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

def slideupdate(self, value):
    props = bpy.context.scene.hisanimvars
    if props.dragging:
        props.activeface.data[self.name] = self.originalval + self.value
        pass
    else:
        self.originalval = props.activeface.data[self.name]
        props.activeslider = self.name
        props.dragging = True
        bpy.ops.hisanim.dragsub('INVOKE_DEFAULT')
    return None

class faceslider(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    value: bpy.props.FloatProperty(name='', default=0.0)
    split: bpy.props.BoolProperty(name='')
    originalval: bpy.props.FloatProperty()

class hisanimvars(bpy.types.PropertyGroup): # list of properties the addon needs. Less to write for registering and unregistering
    bluteam: bpy.props.BoolProperty(
        name="Blu Team",
        description="Swap classes",
        default = False)
    query: bpy.props.StringProperty(default="")
    cosmeticcompatibility: BoolProperty(
        name="Low Quality (Cosmetic Compatible)",
        description="Use cosmetic compatible bodygroups that don't intersect with cosmetics. Disabling will use SFM bodygroups",
        default = True)
    wrdbbluteam: BoolProperty(
        name="Blu Team",
        description="Swap classes",
        default = False)
    hisanimweapons: BoolProperty(name='Search For Weapons')
    hisanimrimpower: FloatProperty(name='Rim Power',
                                description='Multiply the overall rim boost by this number',
                                default=0.400, min=0.0, max=1.0)
    hisanimscale: bpy.props.BoolProperty(default=False, name='Scale With', description='Scales cosmetics with targets bones. Disabled by default')
    hisanimtarget: bpy.props.PointerProperty(type=bpy.types.Object, poll=bonemerge.IsArmature)
    savespace: bpy.props.BoolProperty(default=True, name='Save Space', description='When enabled, The TF2-Trifecta will link textures from source files')
    autobind: bpy.props.BoolProperty(default=False, name='Auto BoneMerge', description='When enabled, weapons will automatically bind to mercs')
    results: bpy.props.CollectionProperty(type=searchHits)
    searched: bpy.props.BoolProperty()
    tools: bpy.props.EnumProperty(
        items=(
        ('WARDROBE', 'Wardrobe', "Show Wardrobe's tools", 'MOD_CLOTH', 0),
        ('MERCDEPLOYER', 'Merc Deployer', "Show Merc Deployer's tools", 'FORCE_DRAG', 1),
        ('BONEMERGE', 'Bonemerge', "Show Bonemerge's tools", 'GROUP_BONE', 2),
        ('FACEPOSER', 'Face Poser', 'Show the Face Poser tools', 'RESTRICT_SELECT_OFF', 3)
        ),
        name='Tool'
    )
    ddsearch: bpy.props.BoolProperty(default=True, name='')
    ddpaints: bpy.props.BoolProperty(default=True, name='')
    ddmatsettings: bpy.props.BoolProperty(default=True, name='')
    ddfacepanel: bpy.props.BoolProperty(default=True, name='')
    ddrandomize: bpy.props.BoolProperty(default=True, name='')
    ddlocks: bpy.props.BoolProperty(default=True, name = '')
    wrinklemaps: bpy.props.BoolProperty(default=True)
    randomadditive: bpy.props.BoolProperty(name = 'Additive', description='Add onto the current face values')
    randomstrength: bpy.props.FloatProperty(name='Random Strength', min=0.0, max=1.0, description='Any random value calculated will be multiplied with this number', default=1.0)
    keyframe: bpy.props.BoolProperty(default=False, name='Keyframe Sliders', description='Keyframe the randomized changes.')
    lockfilter: bpy.props.StringProperty()
    activeslider: bpy.props.StringProperty()
    activeface: bpy.props.PointerProperty(type=bpy.types.Object)
    lastactiveface: bpy.props.PointerProperty(type=bpy.types.Object)
    sliders: bpy.props.CollectionProperty(type=faceslider)
    sliderindex: bpy.props.IntProperty()
    dragging: bpy.props.BoolProperty()

class WDRB_PT_PART1(bpy.types.Panel):
    """A Custom Panel in the Viewport Toolbar""" # for the searching segment.
    bl_label = 'TF2-Trifecta'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'TF2-Trifecta'
    bl_icon = "MOD_CLOTH"

    def draw(self, context):
        prefs = context.preferences.addons[__package__].preferences
        props = bpy.context.scene.hisanimvars
        layout = self.layout
        row = layout.row()
        row.prop(props, 'tools')
        if props.tools == 'WARDROBE':
            row = layout.row()
            row.label(text='Spawn TF2 Cosmetics', icon='MOD_CLOTH')
            row = layout.row()
            row.prop(props, 'query', text="Search", icon="VIEWZOOM")
            row = layout.row()
            row.prop(context.scene.hisanimvars, 'hisanimweapons')
            if props.hisanimweapons:
                row = layout.row()
                row.prop(props, 'autobind')
            layout.label(text="Warning! Don't leave the text field empty!")
            if prefs.missing == True:
                row = layout.row()
                row.label(text='Assets missing. Check preferences for info.')
            row=layout.row()
            row.operator('hisanim.search', icon='VIEWZOOM')
            row=layout.row()
            row.operator('hisanim.clearsearch', icon='X')
            if props.ddmatsettings or not prefs.compactable:
                if prefs.compactable: row = layout.row()
                if prefs.compactable: row.prop(props, 'ddmatsettings', icon='DISCLOSURE_TRI_DOWN', emboss=False)
                if prefs.compactable: row.label(text='Material settings')
                if not prefs.compactable: layout.label(text='Material settings')
                row=layout.row()
                row.operator('hisanim.lightwarps')
                row=layout.row()
                row.operator('hisanim.removelightwarps')
                row = layout.row()
                row.prop(context.scene.hisanimvars, 'hisanimrimpower', slider=True)
                row = layout.row()
                row.prop(context.scene.hisanimvars, 'wrdbbluteam')
            else:
                row = layout.row()
                row.prop(props, 'ddmatsettings', icon='DISCLOSURE_TRI_RIGHT', emboss=False)
                row.label(text='Material settings', icon='MATERIAL')

            if len(context.selected_objects) > 0:
                if context.object.get('skin_groups') != None:
                    row = layout.row()
                    if props.ddpaints or not prefs.compactable:
                        if prefs.compactable: row.prop(props, 'ddpaints', icon='DISCLOSURE_TRI_DOWN', emboss=False)#, text='Paints')
                        if prefs.compactable: row.label(text='Paints')
                        ob = context.object
                        row = layout.row()
                        row.label(text='Attempt to fix material')
                        row = layout.row()
                        row.template_list("MATERIAL_UL_matslots", "", ob, "material_slots", ob, "active_material_index")
                        row = layout.row(align=True)
                        row.operator('hisanim.materialfix')
                        row.operator('hisanim.revertfix')
                        row = layout.row()
                        row.template_icon_view(context.window_manager, 'hisanim_paints', show_labels=True, scale=4, scale_popup=4)
                        row=layout.row(align=True)
                        oper = row.operator('hisanim.paint', text = 'Add Paint')
                        oper.PAINT = newuilist.paints[context.window_manager.hisanim_paints]
                        row.operator('hisanim.paintclear')
                    else:
                        row.prop(props, 'ddpaints', icon='DISCLOSURE_TRI_RIGHT', emboss=False)#, text='Paints')
                        row.label(text='Paints', icon='BRUSH_DATA')
                        #row.prop(props, 'ddpaints', text='Paints', emboss=False)

            if props.searched:
                if props.ddsearch or not prefs.compactable:
                    if prefs.compactable: row = layout.row()
                    if prefs.compactable: row.prop(props, 'ddsearch', icon='DISCLOSURE_TRI_DOWN', emboss=False)
                    if prefs.compactable: row.label(text='Search Results')
                    if not prefs.compactable: layout.label(text='Search Results')
                    hits = props.results
                    split = layout.split(factor=0.2)
                    row = layout.row()
                    if len(hits) > 0:
                        if len(hits) == 1:
                            row.label(text=f'{len(hits)} Result')
                        else:
                            row.label(text=f'{len(hits)} Results')
                        for ops in hits:
                            # draw the search results as buttons
                            split=layout.split(factor=0.2)
                            row=split.row()
                            row.label(text=ops.name.split("_-_")[1])
                            row = split.row()
                            OPER = row.operator('hisanim.loadcosmetic', text=ops.name.split('_-_')[0])
                            OPER.LOAD = ops.name
                            #row.operator()
                    else: 
                        layout = self.layout
                        layout.label(text='Nothing found!')
                else:
                    row = layout.row()
                    row.prop(props, 'ddsearch', icon='DISCLOSURE_TRI_RIGHT', emboss=False)#, text='Paints')
                    row.label(text='Search Results', icon='VIEWZOOM')
        
        if props.tools == 'MERCDEPLOYER':
            row = layout.row()
            row.label(text='Deploy Mercenaries', icon='FORCE_DRAG')
            cln = ["IK", "FK"]
            mercs = ['scout', 'soldier', 'pyro', 'demo',
                    'heavy', 'engineer', 'medic', 'sniper', 'spy']
            if prefs.hisanim_paths.get('TF2-V3') != None:
                if prefs.hisanim_paths.get('TF2-V3').this_is != 'FOLDER':
                    row = layout.row()
                    row.label('TF2-V3 contains an invalid path!')
                else:
                    row = layout.row()
                    row.label(text='Move face in custom properties under data tab.')
                    row = layout.row(align=True)
                    for i in mercs:
                        row.label(text=i)
                        col = layout.column()
                        for ii in cln:
                            MERC = row.operator('hisanim.loadmerc', text=ii)
                            MERC.merc = i
                            MERC.type = ii
                        row = layout.row(align=True)
                    row.prop(context.scene.hisanimvars, "bluteam")
                    row = layout.row()
                    row.prop(context.scene.hisanimvars, "cosmeticcompatibility")
                    row = layout.row()
                    row.prop(props, 'wrinklemaps', text='Wrinkle Maps')
                    
            else:
                row = layout.row()
                row.label(text='TF2-V3 has not been added!')
                row = layout.row()
                row.label(text='If it is added, check name.')
            
        if props.tools == 'BONEMERGE':
            row = layout.row()
            row.label(text='Attach TF2 cosmetics.', icon='DECORATE_LINKED')
            ob = context.object
            row = layout.row()
            self.layout.prop_search(context.scene.hisanimvars, "hisanimtarget", bpy.data, "objects", text="Link to", icon='ARMATURE_DATA')
            
            row = layout.row()
            row.operator('hisanim.attachto', icon="LINKED")
            row=layout.row()
            row.operator('hisanim.detachfrom', icon="UNLINKED")
            row = layout.row()
            row.prop(context.scene.hisanimvars, 'hisanimscale')
            row = layout.row()
            row.label(text='Bind facial cosmetics')
            row = layout.row()
            row.operator('hisanim.bindface')
            row = layout.row()
            row.label(text='Attempt to fix cosmetic')
            row = layout.row()
            row.operator('hisanim.attemptfix')

        if props.tools == 'FACEPOSER':
            rNone = False
            if len(context.selected_objects) == 0: rNone = True
            if rNone: 
                layout.label(text='Select a face!')
                return None
            if context.object.type == 'EMPTY': rNone = True
            if context.object.data.get('aaa_fs') == None: rNone = True
            if rNone:
                layout.label(text='Select a face!')
                return None
            
            if props.ddfacepanel or not prefs.compactable:
                if prefs.compactable:
                    row = layout.row()
                    row.prop(props, 'ddfacepanel', icon='DISCLOSURE_TRI_DOWN', emboss=False)
                    row.label(text='Face Poser')
                
                #layout.row().template_list('HISANIM_UL_SLIDERS', 'Sliders', props, 'sliders', props, 'sliderindex')
                
            else:
                row = layout.row()
                row.prop(props, 'ddfacepanel', icon='DISCLOSURE_TRI_RIGHT', emboss=False)
                row.label(text='Face Poser')
            if props.ddrandomize or not prefs.compactable:
                if prefs.compactable:
                    row = layout.row()
                    row.prop(props, 'ddrandomize', icon='DISCLOSURE_TRI_DOWN', emboss=False)
                    row.label(text='Face Randomizer')
                row = layout.row()
                row.prop(props, 'keyframe')
                row = layout.row()
                row.prop(props, 'randomadditive')
                row = layout.row()
                row.prop(props, 'randomstrength', slider=True)
                row =layout.row()
                op = row.operator('hisanim.randomizeface')
                op.reset = False
                row = layout.row()
                set0 = row.operator('hisanim.randomizeface', text='Reset Face')
                set0.reset = True
                row = layout.row()
                row.prop(context.object.data, '["aaa_fs"]')
            else:
                row = layout.row()
                row.prop(props, 'ddrandomize', icon='DISCLOSURE_TRI_RIGHT', emboss=False)
                row.label(text='Face Randomizer')

            if props.ddlocks or not prefs.compactable:
                if prefs.compactable:
                    row = layout.row()
                    row.prop(props, 'ddlocks', icon='DISCLOSURE_TRI_DOWN', emboss=False)
                    row.label(text='Lock Sliders')
                data = context.object.data
                if data.get('locklist') == None:
                    layout.row().label(text='Locking will prevent randomizing.')
                row = layout.row()
                
                row.prop(props, 'lockfilter', text='Filter')
                box = layout.box()
                for i in data.keys():
                    try:
                        data.id_properties_ui(i)
                        if props.lockfilter not in i: raise
                    except:
                        continue
                    row = box.row(align=True)
                    states = data.get('locklist')
                    if states == None:
                        state = False
                    else:
                        state = states.get(i)
                        if state == None: state = False
                    split = row.split(factor=0.2, align=True)
                    op = split.operator('hisanim.lock', icon='LOCKED' if state else 'UNLOCKED', emboss=False, text='')
                    op.datapath = bpy.context.object.name
                    op.key = i
                    split.prop(data, f'["{i}"]', text=i)
                    '''split = row.split(factor=0.8, align=True)
                    op = split.operator('hisanim.lock', text=i, depress=state)
                    op.datapath = bpy.context.object.name
                    op.key = i
                    split.prop(data, f'["{i}"]', text='', )
                    op = row.operator('hisanim.lock', icon='LOCKED' if state else 'UNLOCKED', emboss=False, text='')
                    op.datapath = bpy.context.object.name
                    op.key = i'''
            else:
                row = layout.row()
                row.prop(props, 'ddlocks', icon='DISCLOSURE_TRI_RIGHT', emboss=False)
                row.label(text='Lock Sliders')
            #props.lastactiveface = props.activeface
            
class HISANIM_OT_LOAD(bpy.types.Operator):
    LOAD: bpy.props.StringProperty(default='')
    bl_idname = 'hisanim.loadcosmetic'
    bl_label = 'Cosmetic'
    bl_description = f'Load this cosmetic into your scene'
    bl_options = {'UNDO'}

    def execute(self, context):
        D = bpy.data
        CLASS = self.LOAD.split("_-_")[1]
        COSMETIC = self.LOAD.split("_-_")[0]

        prefs = context.preferences.addons[__name__].preferences
        paths = prefs.hisanim_paths
        if (p := paths.get(CLASS)) == None:
            self.report({'ERROR'}, f'Directory for "{CLASS}" not found! Make sure an entry for it exists in the addon preferences!')
            return {'CANCELLED'}
        p = p.path
        if not os.path.exists(p):
            self.report({'ERROR'}, f'Entry for "{CLASS}" exists, but the path is invalid!')
        cos = COSMETIC
        with bpy.data.libraries.load(p, assets_only=True) as (file_contents, data_to):
            data_to.objects = [cos]
        list = [i.name for i in D.objects if not "_ARM" in i.name and cos in i.name]
        justadded = D.objects[sorted(list)[-1]]
        skins = justadded.get('skin_groups')
        count = 0
        # updates the skin_groups dictionary on the object with its materials
        # previously it would iterate through the skin_groups dictionary, but this would not work if there were more entries than
        # material slots. it will now only iterate through the minimum between how many material slots there are and how many entries there are.
        for num in range(min(len(justadded.material_slots), len(skins))):
            Range = count + len(skins[str(num)]) # make a range between the last range (0 if first iteration) and the last range + how many entries are in this skin group
            newmatlist = []
            for i in range(count, Range):
                newmatlist.append(justadded.material_slots[i].material.name)
            skins[str(num)] = newmatlist
            count = Range
        justadded['skin_groups'] = skins
        del newmatlist, Range, count, skins, list

        if (wardcol := context.scene.collection.children.get('Wardrobe')) == None:
            wardcol = bpy.data.collections.new('Wardrobe')
            context.scene.collection.children.link(wardcol)
        
        justaddedParent = justadded.parent
        wardcol.objects.link(justaddedParent) # link everything and its children to the 'Wardrobe' collection for better management.
        justaddedParent.use_fake_user = False

        for child in justaddedParent.children:
            wardcol.objects.link(child)
            child.use_fake_user = False

        justaddedParent.location = context.scene.cursor.location

        for mat in justadded.material_slots:
            for NODE in mat.material.node_tree.nodes:
                if NODE.name == 'VertexLitGeneric':
                    NODE.inputs['rim * ambient'].default_value = 1 # for better colors
                    NODE.inputs['$rimlightboost [value]'].default_value = NODE.inputs['$rimlightboost [value]'].default_value* context.scene.hisanimvars.hisanimrimpower
                if Collapse(NODE, 'VertexLitGeneric') == 'continue': # use VertexLitGeneric-WDRB, recursively remove nodes and node groups from VertexLitGeneric
                    continue
                if NODE.type == 'TEX_IMAGE':
                    if ReuseImage(NODE, p) == 'continue': # use existing images
                        continue
        if bpy.context.scene.hisanimvars.wrdbbluteam: # this one speaks for itself
            var = False
            print("BLU")
            try:
                SKIN = justadded['skin_groups']
                OBJMAT = justadded.material_slots
                for i in SKIN: # return where blu materials are found as BLU
                    for ii in SKIN[i]:
                        if "blu" in ii:
                            BLU = i
                            print(BLU)
                            var = True
                            break
                    if var: break
                else: raise
                print(SKIN[BLU])
                for i in enumerate(SKIN[BLU]): # set the materials as BLU
                    print(i)
                    OBJMAT[i[0]].material = bpy.data.materials[i[1]]
                del SKIN, OBJMAT
            except:
                pass

        if bpy.context.object == None: return {'FINISHED'}

        select = bpy.context.object
        # if a Bonemerge compatible rig or mesh parented to one is selected, automatically bind the cosmetic
        # to the rig.

        if select.parent != None:
            select.select_set(False)
            select = select.parent
        
        if select.get('BMBCOMPATIBLE') != None and (context.scene.hisanimvars.autobind if context.scene.hisanimvars.hisanimweapons else True): # if the selected armature is bonemerge compatible, bind to it.
            bak = context.scene.hisanimvars.hisanimtarget
            context.scene.hisanimvars.hisanimtarget = select
            justadded.parent.select_set(True)
            bpy.ops.hisanim.attachto()
            context.scene.hisanimvars.hisanimtarget = bak
            del bak
        
        mercdeployer.PurgeNodeGroups()
        mercdeployer.PurgeImages()
        return {'FINISHED'}

class HISANIM_OT_Search(bpy.types.Operator):
    bl_idname = 'hisanim.search'
    bl_label = 'Search for cosmetics'
    bl_description = "Go ahead, search"
    
    def execute(self, context):
        context.scene.hisanimvars.results.clear()
        context.scene.hisanimvars.searched = True
        lookfor = bpy.context.scene.hisanimvars.query
        lookfor = lookfor.split("|")
        lookfor.sort()
        hits = returnsearch(lookfor)
        for hit in hits:
            new = context.scene.hisanimvars.results.add()
            new.name = hit
        return {'FINISHED'}

class HISANIM_OT_ClearSearch(bpy.types.Operator): # clear the search
    bl_idname = 'hisanim.clearsearch'
    bl_label = 'Clear Search'
    bl_description = 'Clear your search history'
    
    def execute(self, context):
        
        context.scene.hisanimvars.results.clear()
        context.scene.hisanimvars.searched = False
        return {'FINISHED'}

class HISANIM_OT_MATFIX(bpy.types.Operator):
    bl_idname = 'hisanim.materialfix'
    bl_label = 'Fix Material'
    bl_description = 'Fix Material'
    
    def execute(self, context):
        MAT = context.object.active_material

        if MAT.node_tree.nodes.get('WRDB-MIX') != None:
            return {'CANCELLED'}

        NODEMIX = MAT.node_tree.nodes.new('ShaderNodeMixRGB')
        NODEMIX.name = 'WRDB-MIX'
        NODEMIX.location = Vector((-400, 210))
        NODEGAMMA = MAT.node_tree.nodes.new('ShaderNodeGamma')
        NODEGAMMA.name = 'WRDB-GAMMA'
        NODEGAMMA.location = Vector((-780, 110))
        NODEGAMMA.inputs[0].default_value = list(MAT.node_tree.nodes['VertexLitGeneric'].inputs['$color2 [RGB field]'].default_value)
        MAT.node_tree.nodes['VertexLitGeneric'].inputs['$color2 [RGB field]'].default_value = [1, 1, 1, 1]
        NODEGAMMA.inputs[1].default_value = 2.2
        MATLINK = MAT.node_tree.links
        MATLINK.new(MAT.node_tree.nodes['$basetexture'].outputs['Alpha'], NODEMIX.inputs[0])
        MATLINK.new(MAT.node_tree.nodes['$basetexture'].outputs['Color'], NODEMIX.inputs[1])
        MATLINK.new(NODEGAMMA.outputs[0], NODEMIX.inputs[2])
        MATLINK.new(NODEMIX.outputs[0], MAT.node_tree.nodes['VertexLitGeneric'].inputs['$basetexture [texture]'])
        return {'FINISHED'}

class HISANIM_OT_REVERTFIX(bpy.types.Operator):
    bl_idname = 'hisanim.revertfix'
    bl_label = 'Revert Fix'
    bl_description = 'Revert a material fix done on a material'

    def execute(self, context):
        MAT = context.object.active_material
        MATLINK = MAT.node_tree.links
        if MAT.node_tree.nodes.get('WRDB-MIX') != None:
            MAT.node_tree.nodes['VertexLitGeneric'].inputs['$color2 [RGB field]'].default_value = list(MAT.node_tree.nodes['WRDB-GAMMA'].inputs[0].default_value)

            MAT.node_tree.nodes.remove(MAT.node_tree.nodes['WRDB-MIX'])
            MAT.node_tree.nodes.remove(MAT.node_tree.nodes['WRDB-GAMMA'])
            MATLINK.new(MAT.node_tree.nodes['$basetexture'].outputs[0], MAT.node_tree.nodes['VertexLitGeneric'].inputs[0])
            return {'FINISHED'}
        else:
            return {'CANCELLED'}

class HISANIM_OT_PAINTS(bpy.types.Operator):
    bl_idname = 'hisanim.paint'
    bl_label = 'Paint'
    bl_description = 'Use this paint on cosmetic'
    bl_options = {'UNDO'}

    PAINT: bpy.props.StringProperty(default='')

    def execute(self, context):
        paintvalue = self.PAINT.split(' ')
        paintlist = [int(i)/255 for i in paintvalue]
        paintlist.append(1.0)
        MAT = context.object.active_material
        if MAT.node_tree.nodes.get('DEFAULTPAINT') == None: # check if the default paint rgb node exists. if not, create the backup.
            RGBBAK = MAT.node_tree.nodes.new(type='ShaderNodeRGB')
            RGBBAK.name = 'DEFAULTPAINT'
            RGBBAK.location = Vector((-650, -550))
            RGBBAK.label = 'DEFAULTPAINT'
            if not MAT.node_tree.nodes.get('WRDB-GAMMA') == None: # set the backup color.
                RGBBAK.outputs[0].default_value = list(MAT.node_tree.nodes['WRDB-GAMMA'].inputs[0].default_value)
            else:
                RGBBAK.outputs[0].default_value = list(MAT.node_tree.nodes['VertexLitGeneric'].inputs['$color2 [RGB field]'].default_value)
        try: # set the selected paint.
            MAT.node_tree.nodes['WRDB-GAMMA'].inputs[0].default_value = paintlist
        except:
            MAT.node_tree.nodes['VertexLitGeneric'].inputs['$color2 [RGB field]'].default_value = paintlist
        return {'FINISHED'}
    
class HISANIM_OT_PAINTCLEAR(bpy.types.Operator):
    bl_idname = 'hisanim.paintclear'
    bl_label = 'Clear Paint'
    bl_description = 'Clear Paint'
    bl_options = {'UNDO'}

    def execute(self, context):
        MAT = context.object.active_material.node_tree
        if MAT.nodes.get('DEFAULTPAINT') == None: # check if the default paint color exists. if not, assume no paint is applied.
            return {'CANCELLED'}
        if not MAT.nodes.get('WRDB-GAMMA') == None: # set the default color.
            MAT.nodes['WRDB-GAMMA'].inputs[0].default_value = list(MAT.nodes['DEFAULTPAINT'].outputs[0].default_value)
        else:
            MAT.nodes['VertexLitGeneric'].inputs['$color2 [RGB field]'].default_value = list(MAT.nodes['DEFAULTPAINT'].outputs[0].default_value)
        MAT.nodes.remove(MAT.nodes['DEFAULTPAINT'])
        return {'FINISHED'}

classes = [
            searchHits,
            faceslider,
            hisanimvars,
            WDRB_PT_PART1,
            HISANIM_OT_SLIDERESET,
            HISANIM_OT_PAINTCLEAR,
            HISANIM_OT_LOAD,
            HISANIM_OT_PAINTS,
            HISANIM_OT_AddLightwarps,
            HISANIM_OT_RemoveLightwarps,
            HISANIM_OT_Search,
            HISANIM_OT_ClearSearch,
            HISANIM_OT_REVERTFIX,
            HISANIM_OT_MATFIX,
            HISANIM_UL_SLIDERS
            ]
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    mercdeployer.register()
    bpy.types.Scene.hisanimvars = bpy.props.PointerProperty(type=hisanimvars)
    icons.register()
    updater.register()
    newuilist.register()
    preferences.register()
    bonemerge.register()
    #bpy.app.handlers.depsgraph_update_post.append(updatefaces)
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    mercdeployer.unregister()
    icons.unregister()
    updater.unregister()
    newuilist.unregister()
    preferences.unregister()
    bonemerge.unregister()
    del bpy.types.Scene.hisanimvars
    #bpy.app.handlers.depsgraph_update_post.remove(updatefaces)
if __name__ == '__main__':
    register()