import json
import math
import unittest
import sys
from pathlib import Path
from copy import deepcopy
from zipfile import ZipFile
from io import BytesIO

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import generate as g
S=json.loads((ROOT/'assumptions.json').read_text('utf-8'))

class P0ProvisionalTests(unittest.TestCase):
    def test_explicit_hypothetical_provenance(self):
        self.assertEqual(S['disposition'],'HYPOTHETICAL_UNMEASURED_HOLD')
        self.assertTrue(S['constraints']['not_measured'])
        self.assertFalse(S['constraints'].get('claimed_real_measurement',False))
        self.assertEqual(S['provenance']['source_commit'],'a15388ebf2391807559d7cfb334a15c9f3f57992')
    def test_seven_exactly(self): self.assertEqual(len(g.spec_validate(S)),7)
    def test_compression_never_below_floor_width(self):
        d=g.spec_validate(S)
        self.assertGreaterEqual(d['mouth_inner_width']-2*d['compression_wall_travel_each_side'],d['floor_inner_width'])
    def test_removal_travel_exceeds_length(self):
        d=g.spec_validate(S)
        self.assertGreater(d['removal_clearance_along_45deg_axis'],d['trough_length'])
    def test_reject_measured_promotion(self):
        s=deepcopy(S);s['disposition']='MEASURED';
        with self.assertRaises(AssertionError):g.spec_validate(s)
    def test_reject_bad_angled_travel(self):
        s=deepcopy(S);s['measurements']['compression_wall_travel_each_side']=30;
        with self.assertRaises(AssertionError):g.spec_validate(s)
    def test_developed_side_and_a3_cut_pattern(self):
        d=g.spec_validate(S)
        actual=math.hypot(d['wall_vertical_height'],(d['mouth_inner_width']-d['floor_inner_width'])/2)
        self.assertAlmostEqual(actual,70.858,places=2)
        svg=g.sheet_svg(S)
        self.assertIn('width="420mm" height="297mm"',svg)
        self.assertIn('100 mm (measure this)',svg)
        self.assertIn('HYPOTHETICAL',svg)
    def test_concept_cross_section_exists(self):
        s=g.profile_svg(S)
        self.assertIn('mouth 140 mm',s)
        self.assertIn('floor 118 mm',s)
        self.assertIn('height 70 mm',s)
        self.assertIn('NOT measured',s)
    def test_distinct_bays_with_separate_source(self):
        model=g.voxel_model(S)
        self.assertTrue(any(role=='left_floor' for _,role in model.values()))
        self.assertTrue(any(role=='right_floor' for _,role in model.values()))
        self.assertTrue(any(role=='spare_removed_tray_floor' for _,role in model.values()))
        self.assertTrue(any(role=='center_fixed_divider' for _,role in model.values()))
    def test_minecraft_commands_bounded_and_nonexecuting(self):
        f=g.minecraft_functions(S)
        self.assertIn('keep',f['build'])
        self.assertTrue(f['build'].count('setblock')>1000)
        self.assertNotIn('execute as',f['build'])
        self.assertNotIn('summon',f['build'])
        self.assertNotIn('fill ~',f['build'])
        self.assertIn('CONTROL INDICATOR ONLY',f['press_high'])
        self.assertEqual(f['press_high'].count('setblock'),4)
    def test_old_version_has_plural_functions(self):
        z=ZipFile(BytesIO(g.datapack(S,'1.20.1')))
        self.assertIn('data/nutoaster_p0/functions/build.mcfunction',z.namelist())
        self.assertEqual(json.loads(z.read('pack.mcmeta'))['pack']['pack_format'],15)
        self.assertEqual(json.loads(z.read('SOURCE_GUESSES.json'))['status'],'HYPOTHETICAL_UNMEASURED_HOLD')
    def test_modern_version_has_singular_function(self):
        z=ZipFile(BytesIO(g.datapack(S,'26.1.1')))
        self.assertIn('data/nutoaster_p0/function/build.mcfunction',z.namelist())
        self.assertEqual(json.loads(z.read('pack.mcmeta'))['pack']['min_format'],[101,0])
    def test_deterministic_artifact_bytes(self):
        self.assertEqual(g.datapack(S,'1.20.1'),g.datapack(S,'1.20.1'))
        self.assertEqual(g.datapack(S,'26.1.1'),g.datapack(S,'26.1.1'))
    def test_parametric_presets_change_game_geometry(self):
        base=g.voxel_model(S)
        for dims in [(150,125,75,230,10,280,12),(125,107,65,210,8,250,8)]:
            obj=deepcopy(S)
            for k,v in zip(obj['measurements'],dims):obj['measurements'][k]=v
            self.assertEqual(len(g.spec_validate(obj)),7)
            self.assertNotEqual(len(g.voxel_model(obj)),len(base))
            z=ZipFile(BytesIO(g.datapack(obj,'1.20.1')))
            self.assertEqual(json.loads(z.read('SOURCE_GUESSES.json'))['design_intent_source']['measurements'],obj['measurements'])

    def test_expected_source_precision_preserved(self):
        z=ZipFile(BytesIO(g.datapack(S,'26.1.1')))
        obj=json.loads(z.read('SOURCE_GUESSES.json'))
        self.assertEqual(obj['design_intent_source']['measurements'],S['measurements'])
        self.assertTrue(all(not v for v in obj['nonclaims'].values()))
    def test_intent_only_no_heating_or_mechanical_movement(self):
        f=g.minecraft_functions(S)
        for name in f:
            self.assertNotIn('redstone_block',f[name])
            self.assertNotIn('fire',f[name])
            self.assertNotIn('lava',f[name])
        for key in ['GHoT_execution','reLATTE_admission','real_world_authority']:
            self.assertIs(json.loads(ZipFile(BytesIO(g.datapack(S))).read('SOURCE_GUESSES.json'))['nonclaims'][key],False)

if __name__=='__main__': unittest.main()
