#!/usr/bin/env python3
"""NuToaster 003: openly hypothetical P0 dimensions -> cold cardboard sheet and Minecraft model.

Python 3.10+ standard library only. The size hypotheses are NOT sourced measurements;
source SVG is concept art, not orthographic CAD. The model has NO simulated heat, electric
power, spring force, food safety, or fabrication authority. Nothing runs in a Minecraft
world unless a separate operator deliberately installs and calls the function.
"""
from __future__ import annotations
import hashlib, io, json, math, sys, zipfile, argparse
from pathlib import Path
from xml.sax.saxutils import escape

SCHEMA = 'apk.nutoaster.provisional-p0-dimensions/v1'
GAME_NAMESPACE = 'nutoaster_p0'
VOXEL_MM = 10
VERSION_INFO = {'1.20.1': (15, 'functions'), '26.1.1': (101, 'function')}
SPEC_PATH = Path(__file__).with_name('assumptions.json')


def spec_validate(raw: dict) -> dict:
    assert isinstance(raw, dict) and raw.get('schema') == SCHEMA, 'Unknown source schema'
    assert raw.get('disposition') == 'HYPOTHETICAL_UNMEASURED_HOLD', 'Never promote assumptions to measurements'
    d = raw.get('measurements')
    assert isinstance(d, dict) and set(d) == {
        'mouth_inner_width','floor_inner_width','wall_vertical_height','trough_length',
        'insertion_clearance_each_side','removal_clearance_along_45deg_axis',
        'compression_wall_travel_each_side'}, 'Exactly seven invented measurements required'
    for k, v in d.items():
        assert type(v) in (int, float) and math.isfinite(v) and 0 < v < 1000, 'Invalid size: '+k
    assert 90 <= d['mouth_inner_width'] <= 250
    assert 70 <= d['floor_inner_width'] < d['mouth_inner_width']
    assert 25 <= d['wall_vertical_height'] <= 150
    assert 120 <= d['trough_length'] <= 500
    assert 0 < d['insertion_clearance_each_side'] <= 30
    assert d['removal_clearance_along_45deg_axis'] >= d['trough_length']
    assert 0 < d['compression_wall_travel_each_side'] < d['mouth_inner_width']/2
    assert d['mouth_inner_width']-2*d['compression_wall_travel_each_side'] >= d['floor_inner_width'], 'Travel overcloses floor geometry'
    assert raw.get('source_hypothesis',{}).get('trough_inclination_degrees') == 45
    assert raw.get('constraints',{}).get('not_measured') is True
    return d


def source_digest(spec: dict) -> str:
    return hashlib.sha256(json.dumps(spec,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()


def sheet_svg(spec: dict) -> str:
    """An open-ended P0 fold-up cardboard trough, actual 1:1 in A3 landscape mm.

    Floor panel + 2 sloped-side panels. No end caps or spring parts. This is a
    paper/cardboard shape study, not a sheet-metal flat pattern with bend allowance.
    """
    d=spec_validate(spec)
    floor=d['floor_inner_width']; mouth=d['mouth_inner_width']; wall=d['wall_vertical_height']; length=d['trough_length']
    half_spread=(mouth-floor)/2
    developed_side=math.hypot(wall, half_spread)
    net= floor+2*developed_side
    assert length < 260 and net < 290, 'P0 template exceeds current A3 layout'
    x=17; y=29
    fx=x+developed_side; rx=fx+floor; end=x+net
    # Physical measurement bar allows printer scale check; SVG has page size in millimeters.
    def line(x1,y1,x2,y2,colour,width=0.4,dash=''):
        return f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="{colour}" stroke-width="{width}" '+(f'stroke-dasharray="{dash}"' if dash else '')+'/>'
    elements=[
      '<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 420 297">',
      '<rect width="420" height="297" fill="white"/>',
      '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#1b2c36}.small{font-size:3.5px}.body{font-size:4px}.head{font-size:8px;font-weight:bold}.sub{font-size:4px;font-weight:bold}</style>',
      '<text x="16" y="11" class="head">NuToaster P0 — Imagined cold trough / A3 1:1</text>',
      '<text x="16" y="18" class="body">HYPOTHETICAL • UNMEASURED • NO HEAT / ELECTRICITY • CARDBOARD ONLY</text>',
      f'<rect x="{x:.3f}" y="{y:.3f}" width="{developed_side:.3f}" height="{length:.3f}" fill="#e5f0f8"/>',
      f'<rect x="{fx:.3f}" y="{y:.3f}" width="{floor:.3f}" height="{length:.3f}" fill="#e1ebe6"/>',
      f'<rect x="{rx:.3f}" y="{y:.3f}" width="{developed_side:.3f}" height="{length:.3f}" fill="#e5f0f8"/>',
      line(x,y,end,y,'#222',0.8),line(x,y+length,end,y+length,'#222',0.8),
      line(x,y,x,y+length,'#222',0.8),line(end,y,end,y+length,'#222',0.8),
      line(fx,y,fx,y+length,'#1269aa',0.6,'2,1'),line(rx,y,rx,y+length,'#1269aa',0.6,'2,1'),
      f'<text x="{(fx+rx)/2:.2f}" y="{y+13:.2f}" text-anchor="middle" class="body">FLOOR {floor:g} mm</text>',
      f'<text x="{(x+fx)/2:.2f}" y="{y+13:.2f}" text-anchor="middle" class="small">SIDE 1</text>',
      f'<text x="{(rx+end)/2:.2f}" y="{y+13:.2f}" text-anchor="middle" class="small">SIDE 2</text>',
      f'<text x="16" y="282" class="small">BLACK: CUT   /   BLUE DASH: FOLD • Open-ended P0 only; no food, grease or liquids.</text>',
      f'<text x="16" y="287" class="small">PRINT AT 100% ACTUAL SIZE. Confirm the 100 mm calibration bar before cutting.</text>',
      line(300,235,400,235,'#111',1.2), line(300,232,300,238,'#111',0.8),line(400,232,400,238,'#111',0.8),
      '<text x="350" y="231" text-anchor="middle" class="body">100 mm (measure this)</text>',
      '<text x="307" y="31" class="sub">SEVEN GUESSES — NOT MEASURED</text>'
    ]
    labels=[('Mouth inside width',mouth),('Floor inside width',floor),('Vertical wall height',wall),('Inside trough length',length),('Insertion each side',d['insertion_clearance_each_side']),('Removal along axis',d['removal_clearance_along_45deg_axis']),('Travel per wall',d['compression_wall_travel_each_side'])]
    for idx,(label,value) in enumerate(labels):
        yy=39+idx*9
        elements.append(f'<text x="307" y="{yy}" class="body">{escape(label)}: {value:g} mm</text>')
    elements.extend([
      f'<text x="307" y="110" class="body">Design angle (from concept): 45°</text>',
      f'<text x="307" y="119" class="body">Developed side: {developed_side:.1f} mm</text>',
      f'<text x="307" y="128" class="body">Net sheet width: {net:.1f} mm</text>',
      '<text x="307" y="142" class="sub">P0 TEST ONLY</text>',
      '<text x="307" y="151" class="small">Fold side panels upward.</text>',
      '<text x="307" y="157" class="small">Tape externally. Try cold objects.</text>',
      '<text x="307" y="163" class="small">Record real dimensions, fit,</text>',
      '<text x="307" y="169" class="small">clearance and removal motion.</text>',
      '<text x="307" y="182" class="small">End caps omitted intentionally.</text>',
      '<text x="307" y="188" class="small">No spring assembly in P0.</text>',
      '<text x="307" y="200" class="small">Not a manufacturable flat pattern,</text>',
      '<text x="307" y="206" class="small">thermal design, or food-safe device.</text>',
      '<text x="307" y="264" class="small">Design source: appliance-prophet-king</text>',
      '<text x="307" y="270" class="small">prototype-001, schematic only.</text>',
      '</svg>'
    ])
    return '\n'.join(elements)


def profile_svg(spec:dict) -> str:
    d=spec_validate(spec)
    w=d['mouth_inner_width']; floor=d['floor_inner_width']; h=d['wall_vertical_height']; leng=d['trough_length']
    left=(w-floor)/2
    # Proper 2D cross-section: mouth at y=66, narrower bottom at y=66+height.
    top_y=66;bottom_y=top_y+h
    poly=f'45,{top_y} {45+left},{bottom_y} {45+left+floor},{bottom_y} {45+w},{top_y}'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="780" height="440" viewBox="0 0 390 220">
<rect width="390" height="220" fill="#fbfbf8"/>
<style>text{{font:10px Arial,sans-serif;fill:#223}} .head{{font:bold 17px Arial}} .note{{font:8px Arial}} .measure{{stroke:#be5338;stroke-width:1;fill:none}} </style>
<text x="15" y="22" class="head">NuToaster: invented dimensions</text>
<text x="15" y="38" class="note">Cross-section schematic — NOT measured — COLD P0 only</text>
<polygon points="{poly}" fill="#dce9ea" stroke="#243c4c" stroke-width="2"/>
<line class="measure" x1="45" y1="54" x2="{45+w}" y2="54"/>
<text x="{45+w/2}" y="49" text-anchor="middle">mouth {w:g} mm</text>
<line class="measure" x1="{45+left}" y1="{bottom_y+13}" x2="{45+left+floor}" y2="{bottom_y+13}"/>
<text x="{45+w/2}" y="{bottom_y+27}" text-anchor="middle">floor {floor:g} mm</text>
<line class="measure" x1="{58+w}" y1="{top_y}" x2="{58+w}" y2="{bottom_y}"/>
<text x="{65+w}" y="{top_y+h/2}">height {h:g} mm</text>
<text x="282" y="78">length: {leng:g} mm</text>
<text x="282" y="94">inclination: 45°</text>
<text x="282" y="110">side insertion: {d['insertion_clearance_each_side']:g} mm</text>
<text x="282" y="126">extraction: {d['removal_clearance_along_45deg_axis']:g} mm</text>
<text x="282" y="142">travel / wall: {d['compression_wall_travel_each_side']:g} mm</text>
<text x="282" y="163" class="note">No heat, springs or food contact.</text>
<text x="282" y="177" class="note">Sketch not a tolerance drawing.</text>
</svg>'''


def voxel_model(spec:dict) -> dict:
    """Approximate geometry at 10 mm per Minecraft block (a deliberately enlarged game model).

    Every new parameter set is independently rounded to a whole block; exact user
    guesses remain in SOURCE_GUESSES.json. This is NOT millimeter-accurate CAD.
    """
    d=spec_validate(spec)
    snap=lambda mm: math.floor(mm/VOXEL_MM+0.5)
    mouth=snap(d['mouth_inner_width'])
    floor=snap(d['floor_inner_width'])
    length=snap(d['trough_length'])
    height=snap(d['wall_vertical_height'])
    assert 9 <= mouth <= 25 and 6 <= floor < mouth
    assert 12 <= length <= 50 and 3 <= height <= 15
    # 1-cell gap on both sides of the 2-cell center fixed structure.
    left=6
    right=left+mouth+4
    center_left=left+mouth+1
    right_outer=right+mouth+1
    spare_left=right_outer+10
    display_z=9+length-1+12
    blocks={}
    def add(x,y,z,b,role):
        k=(x,y,z)
        if k in blocks:
            assert blocks[k][0]==b, f'collision at {k}: {blocks[k][0]} vs {b}'
        else:blocks[k]=(b,role)
    def rect(x0,y0,z0,x1,y1,z1,b,role):
        for x in range(x0,x1+1):
            for y in range(y0,y1+1):
                for z in range(z0,z1+1):add(x,y,z,b,role)
    rect(0,0,4,right_outer+5,0,display_z+2,'minecraft:smooth_stone','display_plinth')
    rect(spare_left-1,0,4,spare_left+mouth+2,0,display_z,'minecraft:polished_deepslate','removed_tray_plinth')
    for z in range(9,9+length):
        y=8+(9+length-1-z)
        for side,base in [('left',left),('right',right)]:
            offset=(mouth-floor)//2
            floor_left=base+offset
            floor_right=floor_left+floor-1
            rect(floor_left,y,z,floor_right,y,z,'minecraft:iron_block',side+'_floor')
            # Taper both side lips from floor width to mouth width, one voxel at a time.
            for rise in range(1,height+1):
                fraction=rise/height
                lipL=round(floor_left+(base-floor_left)*fraction)
                lipR=round(floor_right+(base+mouth-1-floor_right)*fraction)
                add(lipL,y+rise,z,'minecraft:light_gray_concrete',side+'_sidewall')
                add(lipR,y+rise,z,'minecraft:light_gray_concrete',side+'_sidewall')
        # Fixed *symbolic* heat markers; no actual game or physical heat.
        rect(left-2,y+1,z,left-2,y+height-1,z,'minecraft:orange_concrete','outer_heat_marker_left')
        rect(right_outer,y+1,z,right_outer,y+height-1,z,'minecraft:orange_concrete','outer_heat_marker_right')
        rect(center_left,y+1,z,center_left+1,y+height-1,z,'minecraft:cut_copper','center_fixed_divider')
        # Detached duplicate illustrates removal: NOT a third installed bay.
        rect(spare_left+1,y,z,spare_left+floor,y,z,'minecraft:weathered_copper','spare_removed_tray_floor')
        for x in (spare_left,spare_left+mouth-1):
            rect(x,y+1,z,x,y+height,z,'minecraft:light_gray_concrete','spare_removed_tray_wall')
    for z in (9,9+length-1):
        y=8+(9+length-1-z)
        for x in (left,left+mouth-1,right,right+mouth-1):
            rect(x,y+height+1,z,x,y+height+2,z,'minecraft:iron_bars','guide_rods_symbol')
    for x,col in [(7,'minecraft:lime_concrete'),(10,'minecraft:gray_concrete'),(13,'minecraft:gray_concrete'),(16,'minecraft:gray_concrete')]:
        add(x,1,display_z,col,'compression_display_off')
    add(right+2,1,display_z,'minecraft:light_blue_concrete','left_right_control_symbol')
    add(right+6,1,display_z,'minecraft:cyan_concrete','left_right_control_symbol')
    return blocks


def minecraft_functions(spec:dict) -> dict:
    d=spec_validate(spec)
    display_z=9+math.floor(d['trough_length']/VOXEL_MM+0.5)-1+12
    m=voxel_model(spec)
    lines=[
      '# NuToaster 003 — PROVISIONAL DESIGN / GAME MODEL ONLY.',
      '# All sizes invented; 1 Minecraft block ~ 10 mm in the source concept.',
      '# 1:100 game enlargement under standard 1m block interpretation; no measured CAD.',
      '# Disposable empty creative world ONLY. KEEP can leave partial models.',
      '# NO heat, current, pressure, removable animation, or food safety.',
      '# Source assumptions marked HYPOTHETICAL_UNMEASURED_HOLD.'
    ]
    for (x,y,z),(b,_) in sorted(m.items(),key=lambda kv:(kv[0][1],kv[0][2],kv[0][0])):
        lines.append(f'setblock ~{x} ~{y} ~{z} {b} keep')
    functions={'build':'\n'.join(lines)+'\n'}
    for mode in ('off','low','medium','high'):
        mode_colors={'off':'minecraft:lime_concrete','low':'minecraft:yellow_concrete','medium':'minecraft:orange_concrete','high':'minecraft:red_concrete'}
        lines=['# CONTROL INDICATOR ONLY. No compression occurs.']
        for x,mname in [(7,'off'),(10,'low'),(13,'medium'),(16,'high')]:
            block=mode_colors[mode] if mode==mname else 'minecraft:gray_concrete'
            lines.append(f'setblock ~{x} ~1 ~{display_z} {block} replace')
        functions['press_'+mode]='\n'.join(lines)+'\n'
    return functions


def zip_write(z, name:str, content:str):
    # Fixed metadata for deterministic byte-for-byte world cartridges.
    entry=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0))
    entry.compress_type=zipfile.ZIP_DEFLATED
    entry.external_attr=(0o644 << 16)
    z.writestr(entry,content.encode('utf-8'))


def datapack(spec:dict, target='1.20.1') -> bytes:
    spec_validate(spec)
    assert target in VERSION_INFO
    format_num,folder=VERSION_INFO[target]
    metadata={'description':'NuToaster P0 imaginary sizes (NOT measured; NOT powered)'}
    if target=='1.20.1':metadata['pack_format']=format_num
    else:metadata.update({'min_format':[format_num,0],'max_format':[format_num,0]})
    manifest={
      'schema':'apk.nutoaster.minecraft-draft/v1',
      'status':'HYPOTHETICAL_UNMEASURED_HOLD',
      'minecraft_target':target,'source_sha256':source_digest(spec),
      'model_scale_mm_per_minecraft_block':VOXEL_MM,
      'blocks':len(voxel_model(spec)),
      'voxel_placement_bbox':[max(x for x,y,z in voxel_model(spec))+1,max(y for x,y,z in voxel_model(spec))+1,max(z for x,y,z in voxel_model(spec))+1],
      'design_intent_source':spec,
      'nonclaims':{'actual_fabrication':False,'dimension_measurements':False,'heating':False,
                   'mechanical_compression':False,'food_safe':False,'real_world_authority':False,
                   'GHoT_execution':False,'reLATTE_admission':False},
    }
    instructions=('NuToaster P0 — conceptual Minecraft model. DO NOT USE AS ENGINEERING.\n'
       'Invented sizes, represented at 1 block = about 10 mm. Do NOT infer real-world performance.\n'
       'Install ZIP (without extraction) into a NEW EMPTY BACKED-UP creative world datapacks/.\n'
       '/reload ; /datapack list\n'
       'Check the whole block footprint in SOURCE_GUESSES.json is empty and loaded.\n'
       '/execute positioned 0 90 0 run function nutoaster_p0:build\n'
       '/execute positioned 0 90 0 run function nutoaster_p0:press_low\n'
       'Other modes: press_off, press_medium, press_high. Display markers ONLY.\n'
       'No automatic rollback; no execution at load time; build commands use KEEP.\n')
    bio=io.BytesIO()
    with zipfile.ZipFile(bio,'w') as z:
        zip_write(z,'pack.mcmeta',json.dumps({'pack':metadata},sort_keys=True,indent=2)+'\n')
        for name,content in minecraft_functions(spec).items():
            zip_write(z,f'data/{GAME_NAMESPACE}/{folder}/{name}.mcfunction',content)
        zip_write(z,'SOURCE_GUESSES.json',json.dumps(manifest,sort_keys=True,indent=2)+'\n')
        zip_write(z,'README.txt',instructions)
    return bio.getvalue()


def main():
    parser=argparse.ArgumentParser(description='Make hypothetical cold P0 and Minecraft study model; not engineering CAD.')
    parser.add_argument('output',nargs='?',default=str(Path(__file__).parent/'dist'))
    parser.add_argument('--spec',type=Path,default=SPEC_PATH,help='Optional exported HYPOTHETICAL guesses JSON from tweak.html')
    args=parser.parse_args()
    spec=json.loads(args.spec.read_text('utf-8'));d=spec_validate(spec)
    output=Path(args.output)
    output.mkdir(parents=True,exist_ok=True)
    (output/'NuToaster_P0_A3_Cold_Prototype_100pct.svg').write_text(sheet_svg(spec),'utf-8')
    (output/'NuToaster_P0_Dimensions_Concept.svg').write_text(profile_svg(spec),'utf-8')
    (output/'SOURCE_HYPOTHETICAL_DIMENSIONS.json').write_text(json.dumps(spec,indent=2,sort_keys=True)+'\n','utf-8')
    outputs={}
    for target in ('1.20.1','26.1.1'):
        p=output/('NuToaster_003_Provisional_Java_'+target+'.zip')
        p.write_bytes(datapack(spec,target))
        outputs[target]={'filename':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    print(json.dumps({'disposition':spec['disposition'],'input_guesses_mm':d,'physical_template':'A3 at 100%',
                     'model_blocks':len(voxel_model(spec)),'minecraft':outputs},indent=2))

if __name__=='__main__':main()
