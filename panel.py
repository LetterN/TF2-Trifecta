import bpy
from . import bonemerge, mercdeployer, newuilist

def hasKey(obj, slider) -> bool:
        data = obj.data
        if data.animation_data == None:
            return False
        scene = bpy.context.scene
        action = data.animation_data.action
        if action == None:
            return False


        for curv in action.fcurves:
            if (curv.data_path == f'["{slider.name}"]') or (curv.data_path == f'["{slider.L}"]'):
                for point in curv.keyframe_points:
                    if scene.frame_current == point.co.x:
                        return True
        else:
            return False

class HISANIM_UL_SLIDERS(bpy.types.UIList):

    def filter_items(self, context, data, propname):
        props = context.scene.hisanimvars
        items = getattr(data, propname)
        filtered = [self.bitflag_filter_item] * len(items)
        for i, item in enumerate(items):
            if self.filter_name.lower() not in item.name.lower():
                filtered[i] &= ~self.bitflag_filter_item
                
            if props.up or props.mid or props.low:
                
                if item.Type == 'NONE':
                    filtered[i] &= ~self.bitflag_filter_item

                if item.Type == 'UPPER':
                    if not props.up:
                        filtered[i] &= ~self.bitflag_filter_item
                
                if item.Type == 'MID':
                    if not props.mid:
                        filtered[i] &= ~self.bitflag_filter_item

                if item.Type == 'LOWER':
                    if not props.low:
                        filtered[i] &= ~self.bitflag_filter_item

        return filtered, []

    def draw_item(self, context,
            layout, data,
            item, icon,
            active_data, active_propname,
            index):
        props = context.scene.hisanimvars
        isKeyed = hasKey(bpy.context.object, item)
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.row() # used as a little space to set the active item
            if item.split:
                row = layout.row(align=True)
                Name = item.name.split('_')[-1]
                if not item.realvalue:
                    split = row.split(factor=0.7, align=True)
                    split.prop(item, 'value', slider=True, text=Name)
                    split.prop(props, 'LR', slider=True, text='L-R')
                else:
                    row.prop(props.activeface.data, f'["{item.R}"]', text='R')
                    row.prop(props.activeface.data, f'["{item.L}"]', text='L')
                op = row.operator('hisanim.keyslider', icon='DECORATE_KEYFRAME' if isKeyed else 'DECORATE_ANIMATE', text='', depress=isKeyed)
                op.delete = isKeyed
                op.slider = item.name
                row.prop(item, 'realvalue', icon='RESTRICT_VIEW_OFF' if item.realvalue else 'RESTRICT_VIEW_ON', text='')

            else:
                row = layout.row(align=True)
                Name = item.name.split('_')[-1]
                if not item.realvalue:
                    row.prop(item, 'value', slider=True, text=Name)
                else:
                    row.prop(props.activeface.data, f'["{item.name}"]', text=item.name[4:])
                op = row.operator('hisanim.keyslider', icon='DECORATE_KEYFRAME' if isKeyed else 'DECORATE_ANIMATE', text='', depress=isKeyed)
                op.delete = isKeyed
                op.slider = item.name
                row.prop(item, 'realvalue', icon='RESTRICT_VIEW_OFF' if item.realvalue else 'RESTRICT_VIEW_ON', text='')

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text='')

class HISANIM_UL_LOCKSLIDER(bpy.types.UIList):
    def draw_item(self, context,
            layout, data,
            item, icon,
            active_data, active_propname,
            index):
        props = context.scene.hisanimvars
        DATA = props.activeface.data
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item.split:
                split = layout.split(factor=0.2, align=True)
                split.prop(item, 'locked', icon='LOCKED' if item.locked else 'UNLOCKED')
                split.prop(DATA, f'["{item.R}"]', text=item.R[4:])
                split = layout.split(factor=0.2, align=True)
                split.prop(item, 'lockedL', icon='LOCKED' if item.lockedL else 'UNLOCKED')
                split.prop(DATA, f'["{item.L}"]', text=item.L[4:])
                pass
            else:
                split = layout.split(factor=0.2, align=True)
                split.prop(item, 'locked', icon='LOCKED' if item.locked else 'UNLOCKED')
                DATA = bpy.context.object.data
                split.prop(DATA, f'["{item.name}"]', text=item.name[4:])

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text='')

class HISANIM_UL_RESULTS(bpy.types.UIList):
    def draw_item(self, context,
            layout, data,
            item, icon,
            active_data, active_propname,
            index):
        props = context.scene.hisanimvars
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            name = item.name
            split = layout.split(factor=0.2)
            split.label(text=item.name.split('_-_')[1].title())
            op = split.operator('hisanim.loadcosmetic', text=item.name.split('_-_')[0])
            op.LOAD = item.name

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text='')

class TRIFECTA_PT_PANEL(bpy.types.Panel):
    """A Custom Panel in the Viewport Toolbar"""
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
                        layout.row().template_list('HISANIM_UL_RESULTS', 'Results', props, 'results', props, 'resultindex')
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
                    row.label(text='TF2-V3 contains an invalid path!')
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
                    layout.row().prop(context.scene.hisanimvars, "cosmeticcompatibility")
                    layout.row().prop(props, 'wrinklemaps', text='Wrinkle Maps')
                    layout.row().prop(props, 'hisanimrimpower', slider=True)

                    
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
                row = layout.row()
                #row.enabled = True
                row.template_list('HISANIM_UL_SLIDERS', 'Sliders', props, 'sliders', props, 'sliderindex')
                #row.enabled = props.dragging
                op = row.operator('hisanim.fixfaceposer', icon='PANEL_CLOSE' if props.dragging else 'CHECKMARK', text='')
                layout.row().prop(props, 'LR', slider=True)
                row = layout.row(align=True)
                row.prop(props, 'up', text='Upper', toggle=True)
                row.prop(props, 'mid', text='Mid', toggle=True)
                row.prop(props, 'low', text='Lower', toggle=True)
                layout.row().prop(props, 'sensitivity', slider=True, text='Sensitivity')
                layout.row().operator('hisanim.keyeverything')
                
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
                layout.row().template_list('HISANIM_UL_LOCKSLIDER', 'Lock Sliders', props, 'sliders', props, 'sliderindex')
            else:
                row = layout.row()
                row.prop(props, 'ddlocks', icon='DISCLOSURE_TRI_RIGHT', emboss=False)
                row.label(text='Lock Sliders')
            #props.lastactiveface = props.activeface

classes = [
    TRIFECTA_PT_PANEL,
    HISANIM_UL_SLIDERS,
    HISANIM_UL_RESULTS,
    HISANIM_UL_LOCKSLIDER,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

import bpy
from bpy.props import StringProperty, IntProperty, CollectionProperty, BoolProperty
from bpy.types import PropertyGroup, UIList, Operator, Panel


    