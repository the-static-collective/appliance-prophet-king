#!/usr/bin/env python3
"""Create simple inspectable *voxel* orthographic diagrams, not CAD views."""
from pathlib import Path
import html
from generate import build_model,slope

COLORS={
'minecraft:polished_deepslate':'#354355',
'minecraft:smooth_stone':'#abb7be',
'minecraft:iron_block':'#eef3f1',
'minecraft:light_gray_concrete':'#99a9ae',
'minecraft:orange_concrete':'#f38738',
'minecraft:cut_copper':'#bd7757',
'minecraft:iron_bars':'#263c50',
'minecraft:weathered_copper':'#4c9f95',
'minecraft:lime_concrete':'#9fe853',
'minecraft:gray_concrete':'#75818c',
'minecraft:light_blue_concrete':'#74bbd9',
'minecraft:cyan_concrete':'#42aaa9',
}

def main(out:Path):
    m=build_model()
    TOP_LEFT=32; TOP_TOP=132; STEP=12
    X=65;Z=41
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1380" height="800" viewBox="0 0 1380 800">',
    '<rect width="100%" height="100%" fill="#0c1425"/>',
    '<text x="32" y="48" fill="#f0f6f8" font-family="sans-serif" font-size="29" font-weight="bold">NuToaster 001 · Minecraft concept cartridge</text>',
    '<text x="32" y="79" fill="#9cb4c5" font-family="sans-serif" font-size="16">Semantic translation from appliance-prophet-king · arbitrary voxel scale · NOT measured engineering plans</text>',
    '<text x="32" y="112" fill="#ebf2f4" font-family="sans-serif" font-size="19">TOP VIEW (projected highest occupied block per cell)</text>',
    '<rect x="30" y="130" width="782" height="496" rx="8" fill="#172636"/>',
    '<text x="862" y="112" fill="#ebf2f4" font-family="sans-serif" font-size="19">SIDE PROFILE (one angled bay)</text>',
    '<rect x="852" y="130" width="492" height="496" rx="8" fill="#172636"/>']
    top={}
    for (x,y,z),block in m.blocks.items():
        if (x,z) not in top or y>top[(x,z)][0]: top[(x,z)]=(y,block)
    for (x,z),(_,block) in sorted(top.items()):
        parts.append(f'<rect x="{TOP_LEFT+x*STEP}" y="{TOP_TOP+z*STEP}" width="11.4" height="11.4" fill="{COLORS[block]}"/>')
    parts.append('<text x="44" y="658" fill="#d8e4e9" font-family="sans-serif" font-size="16">Installed left bay</text>')
    parts.append('<text x="280" y="658" fill="#d8e4e9" font-family="sans-serif" font-size="16">Installed right bay</text>')
    parts.append('<text x="580" y="658" fill="#9ae2d8" font-family="sans-serif" font-size="16">Detached trough example</text>')
    # profile lines where y comes directly from generator; no false dimensional labels
    SX=877;SY=543;P=13
    for z in range(8,25):
        y=slope(z)
        px=SX+z*P;py=SY-y*P
        parts.append(f'<rect x="{px}" y="{py}" width="{P-1}" height="{P-1}" fill="#eef3f1"/>')
        for yy in [y+1,y+2]:
            parts.append(f'<rect x="{px}" y="{SY-yy*P}" width="{P-1}" height="{P-1}" fill="#a7b9bd"/>')
        for yy in [y+1,y+2,y+3]:
            parts.append(f'<rect x="{px}" y="{SY-yy*P}" width="{P-1}" height="{P-1}" fill="none" stroke="#f38738" stroke-width="1.5"/>')
    parts.append('<text x="870" y="610" fill="#d2dfe8" font-family="sans-serif" font-size="16">Stepped 1:1 slope = ~45° concept</text>')
    parts.append('<text x="870" y="634" fill="#d2dfe8" font-family="sans-serif" font-size="15">NOT physical dimensions or tolerances</text>')
    legend=[('Steel / tray','#eef3f1'),('Outer / center heat SYMBOL','#f38738'),('Divider','#bd7757'),('Detached tray sample','#4c9f95'),('Compression OFF indicator','#9fe853')]
    for i,(name,color) in enumerate(legend):
        x=35+(i%3)*430;y=716+(i//3)*39
        parts.append(f'<rect x="{x}" y="{y-15}" width="22" height="22" rx="3" fill="{color}"/>')
        parts.append(f'<text x="{x+31}" y="{y+1}" fill="#d9e7ee" font-family="sans-serif" font-size="15">{html.escape(name)}</text>')
    parts.append('</svg>')
    out.write_text('\n'.join(parts)+'\n',encoding='utf-8')
    print('Saved',out)

if __name__=='__main__':
    import sys
    main(Path(sys.argv[1] if len(sys.argv)>1 else 'dist/preview.svg'))
