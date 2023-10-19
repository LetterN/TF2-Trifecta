import bpy
from . import newuilist
from bpy.types import (UIList)
from bpy.props import StringProperty, IntProperty, CollectionProperty, BoolProperty, EnumProperty

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

        if context.scene.poselibVars.stage != 'SELECT':
            layout.label(text='Operation in progress.')
            return None

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item.split:
                row = layout.row(align=True)
                if not item.realvalue:
                    split = row.split(factor=0.7, align=True)
                    split.prop(item, 'value', slider=True, text=item.name.split('_')[-1])
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
        if context.scene.poselibVars.stage != 'SELECT':
            layout.row().label(text='Operation in progress.')
            return None
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

class HISANIM_UL_ITEMS(bpy.types.UIList):
    """
    UI list containing items with builtin sorting capabilities
    """
    layout_type = "DEFAULT" # could be "COMPACT" or "GRID"

    merc_filter: bpy.props.EnumProperty(
        items=(
            ("all", "All", 'All classes'),
            ("scout", "Scout", ''),
            ("sniper", "Sniper", ''),
            ("soldier", "Soldier", ''),
            ("pyro", "Pyro", ''),
            ("heavy", "Heavy", ''),
            ("medic", "Medic", ''),
            ("demo", "Demoman", ''),
            ("spy", "Spy", '')
        ),
        name="Class Filter",
        description="Filter item based on classes that can equip it",
        default="all"
    )
    # TODO implement this
    # hide_medals: BoolProperty(name="Hide medals", description="Hide medal cosmetics", default = True)

    def draw_item(self, context,
            layout, data,
            item, icon,
            active_data, active_propname,
            index, flt_flag):
        props = context.scene.hisanimvars

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # TODO: Add merc icons
            layout.label(text=f"({item.name.split('_-_')[1].title()}) {item.name.split('_-_')[0]}", translate=False)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=f"{item.name.split('_-_')[0]}", translate=False)

    def draw_filter(self, context, layout):
        """Use custom filter"""
        layout.separator()
        col = layout.column(align=True)

        row = col.row()
        row1 = row.row(align=True)
        row1.prop(self, 'filter_name', text='', icon='VIEWZOOM')
        row1.prop(self, 'use_filter_invert', text='', icon='ARROW_LEFTRIGHT')
        row2 = row.row(align=True)
        # row = col.row(align=True)
        row2.prop(self, 'use_filter_sort_alpha', text='', icon='VIEWZOOM')
        row2.prop(self, 'use_filter_sort_reverse', text='', icon='ARROW_LEFTRIGHT')
        col.separator()

        split = col.split()
        # TODO: Add merc icons
        split.prop(self, 'merc_filter', text='')
        # TODO categorize all medals if possible
        # split.prop(self, 'hide_medals', text='Hide Medals')
    
    def filter_items(self, context, data, propname):
        helpers = bpy.types.UI_UL_list
        items = getattr(data, propname)

        flt_ordered = []
        flt_flags = []

        # Filtering by name
        if self.filter_name:
            flt_flags = helpers.filter_items_by_name(self.filter_name, self.bitflag_filter_item, items, 
                "name", reverse=self.use_filter_sort_reverse)

        if not flt_flags:
            flt_flags = [self.bitflag_filter_item] * len(items)

        if not (self.merc_filter == "all"):
            for idx, vg in enumerate(items):
                metaname = vg.name.split('_-_')[1]
                if metaname == self.merc_filter or metaname == "weapons":
                    continue
                flt_flags[idx] = ~self.bitflag_filter_item

        return flt_flags, flt_ordered

class HISANIM_UL_USESLIDERS(bpy.types.UIList):
    def filter_items(self, context, data, propname):
        poselib = context.scene.poselibVars
        props = context.scene.hisanimvars
        items = getattr(data, propname)
        filtered = [self.bitflag_filter_item] * len(items)
        for i, item in enumerate(items):
            if self.filter_name.lower() not in item.name.lower():
                filtered[i] &= ~self.bitflag_filter_item
                MATERIAL_UL_matslots_example
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

        sortedItems = bpy.types.UI_UL_list.sort_items_helper([(num, item) for num, item in enumerate(items)], key=lambda a: a[1].use, reverse=True)
        return filtered, sortedItems if poselib.sort else []

    def draw_item(self, context,
            layout, data,
            item, icon,
            active_data, active_propname,
            index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.row() # used as a little space to set the active item
            row = layout.row(align=True)
            row.prop(item, 'use', text='')
            if item.split:
                row.label(text="_".join(item.name.split('_')[2:]))
            else:
                row.label(text="_".join(item.name.split('_')[1:]))

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text='')

class POSELIB_UL_panel(UIList):
    def draw_item(self, context,
            layout, data,
            item, icon,
            active_data, active_propname,
            index):
        props = context.scene.poselibVars
        row = layout.row()
        row.label(text=item.name)
        op = row.operator('poselib.prepareapply', text='', icon='FORWARD')
        op.viseme = item.name

class POSELIB_UL_visemes(UIList):
    def draw_item(self, context,
            layout, data,
            item, icon,
            active_data, active_propname,
            index):
        props = context.scene.poselibVars
        row = layout.row()
        row.prop(item, 'use', text='')
        row.label(text="_".join(item.name.split("_")[1:]))

class LOADOUT_UL_loadouts(UIList):
    def draw_item(self, context,
            layout, data,
            item, icon,
            active_data, active_propname,
            index):
        props = context.scene.hisanimvars
        row = layout.row()
        row.label(text=': '.join(item.name.split('_-_')))
        if props.stage == 'NONE':
            op = row.operator('loadout.select', text='', icon='FORWARD')
            op.loadout = item.name

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
        poselib = bpy.context.scene.poselibVars
        layout = self.layout
        
        # the main "box" containing everything.
        maindiv = layout.box()

        if prefs.quickswitch:
            col = maindiv.box().column(align=True)
            col.label(text=f'Tool: {props.tools.title()}')
            split = col.split(align = True)
            row = col.row()
            split.prop(props, 'wr', icon='MOD_CLOTH', toggle=True)
            split.prop(props, 'md', icon='FORCE_DRAG', toggle=True)
            split.prop(props, 'bm', icon='GROUP_BONE', toggle=True)
            split.prop(props, 'fp', icon='RESTRICT_SELECT_OFF', toggle=True)
        else:
            maindiv.row().prop(props, 'tools')

        if props.tools == 'WARDROBE':
            wardrobe_box = maindiv.box()

            col = wardrobe_box.column()
            col.label(text='Spawn TF2 Cosmetics', icon='MOD_CLOTH')
            
            hits = getattr(props, 'items')
            col = col.column()
            colcol = col.column()   
            colcol.template_list('HISANIM_UL_ITEMS', '', props, 'items', props, 'resultindex')
            
            split = colcol.split(align = True, factor=0.9)
            if not props.resultindex == -1 and len(hits) > 0:
                objname = hits[props.resultindex]
                op = split.operator('hisanim.loadcosmetic', text=f"Equip {objname.name.split('_-_')[0].title()}")
                op.LOAD = objname.name
            else:
                # fake items
                fakedisable = split.row(align = True)
                fakedisable.enabled = False
                fakedisable.operator('hisanim.loadcosmetic', text="Equip None")
            split.operator('hisanim.refresh_item_list', text="", icon="FILE_REFRESH")

            # col.prop(context.scene.hisanimvars, 'hisanimweapons')
            if props.hisanimweapons:
                col.prop(props, 'autobind')

            if prefs.missing == True:
                col.label(text='Some assets missing. Check preferences for info.', icon="INFO")

            material_box = maindiv.box()
            material_row = material_box.row()
            if props.ddmatsettings:
                material_row.prop(props, 'ddmatsettings', icon='DISCLOSURE_TRI_DOWN', emboss=False)
                material_row.label(text='Material settings')
                
                mbox_col=material_box.column(align = True)
                mbox_col.operator('hisanim.lightwarps')
                mbox_col.operator('hisanim.removelightwarps')
                mbox_col.prop(context.scene.hisanimvars, 'hisanimrimpower', slider=True)
                mbox_col.prop(context.scene.hisanimvars, 'wrdbbluteam')
            else:
                material_row.prop(props, 'ddmatsettings', icon='DISCLOSURE_TRI_RIGHT', emboss=False)
                material_row.label(text='Material settings')

            if len(context.selected_objects) > 0 and context.object and context.object.get('skin_groups') != None:
                paint_box = maindiv.box()
                paint_row = paint_box.row()
                if props.ddpaints:
                    paint_row.prop(props, 'ddpaints',  icon='DISCLOSURE_TRI_DOWN', emboss=False)
                    paint_row.label(text='Paints')

                    ob = context.object
                    pbox_col = paint_box.column(align = True)
                    pbox_col.template_icon_view(context.window_manager, 'hisanim_paints', show_labels=True, scale=4, scale_popup=4)
                    pbox_spli = pbox_col.split(align = True)
                    pbox_spli.operator('hisanim.paint', text = 'Add Paint').PAINT = newuilist.paints[context.window_manager.hisanim_paints]
                    pbox_spli.operator('hisanim.paintclear')

                    # TODO should material settings own fixing instead of paints?
                    pbox_fix_col = paint_box.column(align = True)
                    pbox_fix_col.enabled = prefs.compactable
                    # pbox_fix_col.label(text='Attempt to fix material')
                    pbox_fix_col.template_list("MATERIAL_UL_matslots", "", ob, "material_slots", ob, "active_material_index")
                    pbox_fix_spli = pbox_fix_col.split(align = True)
                    pbox_fix_spli.operator('hisanim.materialfix')
                    pbox_fix_spli.operator('hisanim.revertfix')
                else:
                    paint_row.prop(props, 'ddpaints', icon='DISCLOSURE_TRI_RIGHT', emboss=False)
                    paint_row.label(text='Paints', icon='BRUSH_DATA')

            loadout_box = maindiv.box()
            loadout_row = loadout_box.row()
            if props.ddloadouts:
                loadout_row.prop(props, 'ddloadouts', icon='DISCLOSURE_TRI_DOWN', emboss=False)
                loadout_row.label(text='Loadouts')
                
                # should look like the material selection tab
                row = loadout_box.row()
                row.template_list('LOADOUT_UL_loadouts', 'Loadouts', props, 'loadout_data', props, 'loadout_index')
                opcol = row.column()
                opcol1 = opcol.column(align = True)
                opcol1.operator('wdrb.select', text='', icon='ADD')
                opcol1.operator('loadout.remove', text='', icon='REMOVE')
                opcol.operator('loadout.refresh', icon='FILE_REFRESH', text='', emboss=False)
                opcol2 = opcol.column(align = True)
                opcol2.operator('loadout.move', text='', icon='TRIA_UP')
                opcol2.operator('loadout.move', text='', icon='TRIA_DOWN')

                if props.stage == 'SELECT':
                    loadout_new_col = loadout_box.column()
                    if (len(bpy.types.Scene.loadout_temp) == 0): loadout_new_col.label(text='No Cosmetics Selected!', icon="ERROR")
                    loadout_new_col.prop(props, 'loadout_name', text='Name')
                    split = loadout_new_col.split(align = True)
                    split.operator('wdrb.cancel')
                    split.operator('wdrb.confirm')

                if props.stage == 'DISPLAY':
                    split = loadout_box.split(align = True)
                    split.operator('wdrb.cancel')
                    split.operator('loadout.load')
                if props.stage == 'NONE': 
                    loadout_box.operator('loadout.rename')
            else:
                loadout_row.prop(props, 'ddloadouts', icon='DISCLOSURE_TRI_RIGHT', emboss=False)
                loadout_row.label(text='Loadouts', icon='ASSET_MANAGER')
        
        if props.tools == 'MERC DEPLOYER':
            merc_box = maindiv.box()

            merc_box.label(text='Deploy Mercenaries', icon='FORCE_DRAG')
            cln = ["IK", "FK"]
            mercs = ['scout', 'soldier', 'pyro', 'demo', 'heavy', 'engineer', 'medic', 'sniper', 'spy']

            if prefs.hisanim_paths.get('TF2-V3') == None:
                merc_box.label(text='TF2-V3 has not been added!', icon="INFO")
            if prefs.hisanim_paths.get('TF2-V3') and prefs.hisanim_paths.get('TF2-V3').this_is != 'FOLDER':
                merc_box.label(text='TF2-V3 must be a folder!', icon="INFO")

            column = merc_box.column()
            column.enabled = (prefs.hisanim_paths.get('TF2-V3') != None and prefs.hisanim_paths.get('TF2-V3').this_is == 'FOLDER')
            merc_column = column.column(align = True)
            for mercname in mercs:
                mercrow = merc_column.row(align = True)
                mercrow.label(text = mercname.title())
                for ii in cln:
                    MERC = mercrow.operator('hisanim.loadmerc', text=ii)
                    MERC.merc = mercname
                    MERC.rigtype = ii
    
            column.prop(context.scene.hisanimvars, "bluteam")
            column.prop(context.scene.hisanimvars, "cosmeticcompatibility")
            column.prop(props, 'hisanimrimpower', slider=True)
            
        if props.tools == 'BONEMERGE':
            bonemerge_box = maindiv.box()
            bonemerge_box.label(text='Attach TF2 cosmetics.', icon='DECORATE_LINKED')
            bonemerge_box.prop_search(context.scene.hisanimvars, "hisanimtarget", bpy.data, "objects", text="Link to", icon='ARMATURE_DATA')
            
            row = bonemerge_box.row(align = True)
            row.operator('hisanim.attachto', icon="LINKED")
            row.operator('hisanim.detachfrom', icon="UNLINKED")
            
            bonemerge_box.prop(context.scene.hisanimvars, 'hisanimscale')
            bonemerge_box.operator('hisanim.bindface')
            bonemerge_box.operator('hisanim.attemptfix')

        if props.tools == 'FACE POSER':
            face_box = maindiv.box()

            if (len(context.selected_objects) == 0 
                or context.object == None 
                or context.object.type == 'EMPTY' 
                or context.object.data.get('aaa_fs') == None):
                face_box.label(text='Select a face!')
                return None
            
            if props.ddfacepanel or not prefs.compactable:
                if prefs.compactable:
                    row = face_box.row()
                    row.prop(props, 'ddfacepanel', icon='DISCLOSURE_TRI_DOWN', emboss=False)
                    row.label(text='Face Poser')
                contentcol = face_box.column()
                
                row = contentcol.row(align=True)
                row.template_list('HISANIM_UL_SLIDERS', 'Sliders', props, 'sliders', props, 'sliderindex')
                col = row.column()
                col.operator('hisanim.fixfaceposer', icon='PANEL_CLOSE' if props.dragging else 'CHECKMARK', text='')
                col.prop(bpy.context.scene.tool_settings, 'use_keyframe_insert_auto', text='')
                col.label(text='', icon='BLANK1')
                col.operator('hisanim.keyeverything', icon='DECORATE_KEYFRAME', text='')

                row = contentcol.row(align=True)
                op = row.operator('hisanim.adjust', text='', icon='TRIA_LEFT')
                op.amount = -0.1
                row.prop(props, 'LR', slider=True)
                op = row.operator('hisanim.adjust', text='', icon='TRIA_RIGHT')
                op.amount = 0.1
                row = contentcol.row(align=True)
                row.prop(props, 'up', text='Upper', toggle=True)
                row.prop(props, 'mid', text='Mid', toggle=True)
                row.prop(props, 'low', text='Lower', toggle=True)

                contentcol
                row = contentcol.row(align=True)
                row.operator('hisanim.optimize')
                row.operator('hisanim.restore')
            else:
                row = face_box.row()
                row.prop(props, 'ddfacepanel', icon='DISCLOSURE_TRI_RIGHT', emboss=False)
                row.label(text='Face Poser', icon='RESTRICT_SELECT_OFF')

            if props.ddposelib or not prefs.compactable:
                if prefs.compactable:
                    row = layout.row()
                    row.prop(props, 'ddposelib', icon='DISCLOSURE_TRI_DOWN', emboss=False)
                    row.label(text='Pose Library')

                row = layout.row()
                if poselib.stage == 'SELECT':
                    col = row.column()
                    col.template_list('POSELIB_UL_panel', 'Pose Library', poselib, 'visemesCol', poselib, 'activeViseme')
                    col = row.column()
                    col.operator('poselib.prepareadd', text='', icon='ADD')
                    col.operator('poselib.remove', text='', icon='REMOVE')
                    col.operator('poselib.refresh', icon='FILE_REFRESH', text='', emboss=False)
                    op = col.operator('poselib.move', text='', icon='TRIA_UP')
                    op.pos = 1
                    op1 = col.operator('poselib.move', text='', icon='TRIA_DOWN')
                    op1.pos = -1
                    layout.row().operator('poselib.rename')
                if poselib.stage == 'ADD':
                    row.template_list('HISANIM_UL_USESLIDERS', 'Sliders', props, 'sliders', props, 'sliderindex')
                    row = layout.row(align=True)
                    row.prop(poselib, 'sort', toggle=True)
                    row.prop(props, 'up', text='Upper', toggle=True)
                    row.prop(props, 'mid', text='Mid', toggle=True)
                    row.prop(props, 'low', text='Lower', toggle=True)
                    layout.row().prop(poselib, 'name')
                    layout.row().operator('poselib.add')
                    layout.row().operator('poselib.cancel')
                if poselib.stage == 'APPLY':
                    row.label(text=poselib.visemeName)
                    layout.row().template_list('POSELIB_UL_visemes', 'Items', poselib, 'dictVisemes', poselib, 'activeItem')
                    layout.row().prop(poselib, 'value', slider=True)
                    layout.row().prop(poselib, 'keyframe')
                    layout.row().operator('poselib.apply')
                    layout.row().operator('poselib.cancelapply')
            else:
                row = layout.row()
                row.prop(props, 'ddposelib', icon='DISCLOSURE_TRI_RIGHT', emboss=False)
                row.label(text='Pose Library', icon='OUTLINER_OB_GROUP_INSTANCE')
                

            if props.ddrandomize or not prefs.compactable:
                if prefs.compactable:
                    row = layout.row()
                    row.prop(props, 'ddrandomize', icon='DISCLOSURE_TRI_DOWN', emboss=False)
                    row.label(text='Face Randomizer')
                row = layout.row()
                row.prop(props, 'keyframe')
                row.prop(props, 'randomadditive')
                layout.row().prop(props, 'randomstrength', slider=True)
                layout.row().operator('hisanim.randomizeface')
                layout.row().operator('hisanim.resetface')
                layout.row().prop(context.object.data, '["aaa_fs"]', text='Flex Scale')
            else:
                row = layout.row()
                row.prop(props, 'ddrandomize', icon='DISCLOSURE_TRI_RIGHT', emboss=False)
                row.label(text='Face Randomizer', icon='RNDCURVE')

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
                row.label(text='Lock Sliders', icon='LOCKED')

classes = [
    TRIFECTA_PT_PANEL,
    HISANIM_UL_SLIDERS,
    HISANIM_UL_ITEMS,
    HISANIM_UL_LOCKSLIDER,
    POSELIB_UL_panel,
    HISANIM_UL_USESLIDERS,
    POSELIB_UL_visemes,
    LOADOUT_UL_loadouts
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


    
