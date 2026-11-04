#!/usr/bin/env python3
"""NuToaster concept -> Minecraft Java datapack.

This is a semantic visual rehearsal, *not* dimensional reconstruction.
No electrical/thermal/mechanical appliance behavior is modeled.
"""
from __future__ import annotations
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile

SOURCE_REPOSITORY = "the-static-collective/appliance-prophet-king"
SOURCE_BRANCH = "001-nutoaster-prototype"
SOURCE_COMMIT = "a15388ebf2391807559d7cfb334a15c9f3f57992"
SOURCE_SCHEMATIC_BLOB = "ed4c6499eee6b0d477ee25b69a6d477dfbba5238"
SCHEMA = "apk.nutoaster.semantic-minecraft/v1"
NAMESPACE = "nutoaster"
PACK_FORMAT = 101 # Minecraft Java 26.1.1 target (matching Circuit 005)
FLOOR_Z = range(8,25)
CHASSIS = "minecraft:polished_deepslate"
BASE = "minecraft:smooth_stone"
TRAY = "minecraft:iron_block"
TRAY_WALL = "minecraft:light_gray_concrete"
HEATER = "minecraft:orange_concrete" # non-heating visual label
DIVIDER = "minecraft:cut_copper"
ROD = "minecraft:iron_bars"
SPARE = "minecraft:weathered_copper"

class VoxelModel:
    def __init__(self):
        self.blocks = {}
        self.roles = {}
        self.conflicts = []

    def place(self, x:int,y:int,z:int, block:str, role:str):
        assert all(isinstance(c, int) for c in (x,y,z))
        assert 0 <= x <= 64 and 0 <= y <= 28 and 0 <= z <= 40, 'out of model bounds'
        pos=(x,y,z)
        if pos in self.blocks:
            if self.blocks[pos] != block:
                self.conflicts.append((pos,self.blocks[pos],block))
            return
        self.blocks[pos]=block
        self.roles[pos]=role

    def cuboid(self,x1,y1,z1,x2,y2,z2,block,role):
        for x in range(x1,x2+1):
            for y in range(y1,y2+1):
                for z in range(z1,z2+1):
                    self.place(x,y,z,block,role)

def slope(z:int) -> int:
    """Demonstrative ~45-degree stepped centerline, *not* a real measurement."""
    return 5 + (24-z)


def build_model() -> VoxelModel:
    m = VoxelModel()
    # One pedestal for the working two-bay prototype, one nearby for an
    # illustration of an individually removable *spare* trough.
    m.cuboid(3,0,4,44,0,31,BASE,'display_plinth')
    m.cuboid(50,0,4,62,0,31,CHASSIS,'separate_spare_display_plinth')
    # All elevated rails and separators are visualized; orange is not heat.
    for z in FLOOR_Z:
        y=slope(z)
        # common structural rail below each slope, no thermal model
        for x in (8,18,28,38):
            m.place(x,y-1,z,CHASSIS,'chassis_support')
        # fixed left, middle, and right heater/structure markers
        for yy in range(y+1,y+4):
            m.place(6,yy,z,HEATER,'left_fixed_heat_symbol')
            m.place(41,yy,z,HEATER,'right_fixed_heat_symbol')
            m.place(23,yy,z,DIVIDER,'center_structural_divider')
            m.place(24,yy,z,HEATER,'center_fixed_heat_symbol')
        # left bay and right bay: removable *conceptual* troughs
        for xlo, xhi, label in ((10,16,'left'),(30,36,'right')):
            for x in range(xlo,xhi+1):
                m.place(x,y,z,TRAY,label+'_trough_floor')
            for edge in (xlo,xhi):
                for yy in range(y+1,y+3):
                    m.place(edge,yy,z,TRAY_WALL,label+'_trough_wall')
        # detached specimen of one trough (NOT a third cooking bay)
        for x in range(53,60):
            m.place(x,y,z,SPARE,'spare_trough_sample_floor')
        for edge in (53,59):
            for yy in (y+1,y+2):
                m.place(edge,yy,z,TRAY_WALL,'spare_trough_sample_wall')
    # Four guide rods per installed trough, far-side stationary symbols.
    for z in (9,23):
        y=slope(z)
        for x in (10,16,30,36):
            for yy in (y+3,y+4):
                m.place(x,yy,z,ROD,'spring_guides_symbol_only')
    # Front-panel non-electrical mode indicators: OFF highlighted. No heater.
    for x,block in [(9,'minecraft:lime_concrete'),(12,'minecraft:gray_concrete'),
                    (15,'minecraft:gray_concrete'),(18,'minecraft:gray_concrete')]:
        m.place(x,1,34,block,'compression_mode_indicator_off_default')
    # Two separate bay indicators; there is no control circuit.
    m.place(30,1,34,'minecraft:light_blue_concrete','left_bay_marker')
    m.place(36,1,34,'minecraft:cyan_concrete','right_bay_marker')
    assert not m.conflicts, 'overlapping mutually different blocks: '+str(m.conflicts[:6])
    return m


def build_function(model:VoxelModel)->str:
    lines=[
       '# NuToaster 001: *semantic* voxel model, NOT measured CAD.',
       '# Generated from a human-readable experimental repo concept; arbitrary 1:1 voxel scale.',
       '# Run ONLY in a brand-new, empty, disposable creative world.',
       '# All commands use KEEP, so blocks should not replace existing world blocks.',
       '# Keep may make the assembly incomplete if the area is occupied.',
       '# All orange blocks are symbolic; no live heating or electricity.',
       '# Bay contents, trough removal, springs, and heat are NOT functional.',
    ]
    for (x,y,z),block in sorted(model.blocks.items(),key=lambda kv:(kv[0][1],kv[0][2],kv[0][0])):
        lines.append(f'setblock ~{x} ~{y} ~{z} {block} keep')
    return '\n'.join(lines)+'\n'


def indicator_function(mode:str)->str:
    assert mode in ('off','low','medium','high')
    xs=(9,12,15,18)
    colors={'off':'minecraft:lime_concrete','low':'minecraft:yellow_concrete',
            'medium':'minecraft:orange_concrete','high':'minecraft:red_concrete'}
    positions=('off','low','medium','high')
    lines=['# Press modes are DISPLAY-ONLY. No mechanical movement or force.']
    for x,what in zip(xs,positions):
        b=colors[mode] if mode==what else 'minecraft:gray_concrete'
        lines.append(f'setblock ~{x} ~1 ~34 {b} replace')
    return '\n'.join(lines)+'\n'


def manifest(model:VoxelModel):
    roles={}
    for role in model.roles.values():roles[role]=roles.get(role,0)+1
    return {
      'schema':SCHEMA,
      'display_name':'NuToaster 001 — Two Bay Countertop Concept',
      'source':{'repository':SOURCE_REPOSITORY,'branch':SOURCE_BRANCH,'commit':SOURCE_COMMIT,
        'schematic_path':'prototype-001/nutoaster-001.svg','schematic_blob_sha1':SOURCE_SCHEMATIC_BLOB,
        'description_path':'prototype-001/README.md'},
      'source_claims':{'installed_cooking_bays':2,'removable_trough_per_bay':1,
        'trough_angle_hypothesis_degrees':45, 'compression_modes':['OFF','LOW','MEDIUM','HIGH'],
        'default_compression':'OFF', 'fixed_heater_wall_count':3,
        'trough_material_concept':'stainless steel','first_physical_test':'P0 cold cardboard/scrap trough'},
      'interpretation':{'space':'concept-only enlarged voxel teaching model',
        'model_xz_blocks':[65,41],'model_y_blocks':29,
        'voxel_scale':'arbitrary; NOT meters, inches, or fabrication dimensions',
        'angle_representation':'one block vertical per one Z step (visual staircase, not real mechanical angle)',
        'bay_layout':['left','right'],'detached_sample':'illustration of a removable duplicate trough, NOT third cooking bay',
        'mode_functions':'display indicators only; no compression actuation'},
      'voxel_count':len(model.blocks),'component_cells':roles,
      'provenance_disposition':'CONCEPT_ONLY_UNMEASURED_HOLD',
      'safety_and_truth':{
        'mechanical_cad':False,'dimensional_drawing':False,'structural_test':False,
        'thermal_simulation':False,'electrical_safety_test':False,'food_safe_device':False,
        'real_world_construction_authority':False,'gHot_runtime_called':False,'relatte_signed_receipt':False},
      'next_real_measurements':['mouth width','floor width','wall height','trough length',
        'insertion clearance','removal clearance','useful compression-wall travel']
    }


def make_datapack(model:VoxelModel)->bytes:
    m=manifest(model)
    bio=io.BytesIO()
    with zipfile.ZipFile(bio,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        z.writestr('pack.mcmeta',json.dumps({'pack':{
          'description':'NuToaster experimental concept geometry — not measured CAD',
          'min_format':[PACK_FORMAT,0],'max_format':[PACK_FORMAT,0]}},indent=2)+'\n')
        z.writestr(f'data/{NAMESPACE}/function/build.mcfunction',build_function(model))
        for mode in ('off','low','medium','high'):
            z.writestr(f'data/{NAMESPACE}/function/press_{mode}.mcfunction',indicator_function(mode))
        z.writestr('SOURCE_CONCEPT.json',json.dumps(m,indent=2)+'\n')
        z.writestr('README.txt',README)
    return bio.getvalue()

README='''NuToaster Minecraft concept carrier — NOT a dimensional blueprint or construction model.\n\nSOURCE: the-static-collective/appliance-prophet-king, branch 001-nutoaster-prototype\nSOURCE DESIGN: two inclined (~45 degrees) removable steel troughs, 3 fixed heater\nwall/divider regions, optional adjustable guided-spring compression, OFF default.\nMODEL: enlarged arbitrary voxel scale, independent active bays and a detached\nremovable-trough *illustration*, orange means SYMBOLIC HEAT, not real heat.\n\nMinecraft Java target: 26.1.1, datapack format 101.\n\n1. Create an EMPTY disposable FLAT creative test world. BACK IT UP.\n2. Put this entire datapack ZIP in that world's datapacks/ directory.\n3. In Minecraft: /reload ; /datapack list\n4. As a fully authorized operator run, in a clear and fully loaded region:\n   /execute positioned 0 90 0 run function nutoaster:build\n5. Look at the twin angled silver troughs, orange outer heater markers, copper\n   middle divider, guide rods, and detached copper-toned removable-trough sample.\n6. Optional color-panel demonstration functions (NO moving pressure walls):\n   /execute positioned 0 90 0 run function nutoaster:press_off\n   /execute positioned 0 90 0 run function nutoaster:press_low\n   /execute positioned 0 90 0 run function nutoaster:press_medium\n   /execute positioned 0 90 0 run function nutoaster:press_high\n   The row of mode markers is at relative X=9,12,15,18 / Y=1 / Z=34.\n7. Do not copy into a valuable world. No automated rollback. Build uses KEEP,\n   mode display changes only four predesignated cells using REPLACE.\n8. Inspect SOURCE_CONCEPT.json for the exact source reference and all nonclaims.\n\nNothing here is a heated appliance, electrical engineering prototype,\nfood-safe prototype, physical force test, mechanical drawing, measured real\ngeometry, or evidence of any real-world fabrication. A Minecraft 45-degree\nstaircase does not establish 45-degree real-life trough angles.\n\nThe appliance-prophet-king source recommends FIRST a cold P0 full-size physical\ntrough to measure mouth, floor, height, length, insertion/removal clearance,\nand travel. That evidence should replace rather than be inferred from pixels.\n'''


def write_release(output:Path):
    model=build_model()
    output.mkdir(parents=True,exist_ok=True)
    datapack=output/'NuToaster_001_Minecraft_Concept_Java_26.1.1.zip'
    datapack.write_bytes(make_datapack(model))
    (output/'SOURCE_CONCEPT.json').write_text(json.dumps(manifest(model),indent=2)+'\n',encoding='utf-8')
    (output/'README.txt').write_text(README,encoding='utf-8')
    (output/'nutoaster_build.mcfunction').write_text(build_function(model),encoding='utf-8')
    print(json.dumps({'datapack':str(datapack),'sha256':hashlib.sha256(datapack.read_bytes()).hexdigest(),
      'block_count':len(model.blocks),'roles':len(set(model.roles.values())),
      'command_count':len(build_function(model).splitlines())-7},indent=2))

if __name__=='__main__':
    write_release(Path(sys.argv[1] if len(sys.argv)>1 else 'dist'))
