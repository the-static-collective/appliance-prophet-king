import io
import json
from pathlib import Path
import sys
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import generate as g

class NuToasterCartridgeTests(unittest.TestCase):
    def setUp(self):
        self.m = g.build_model()

    def test_two_distinct_installed_bays(self):
        for x0,x1 in [(10,16),(30,36)]:
            for z in g.FLOOR_Z:
                y=g.slope(z)
                self.assertTrue(all(self.m.blocks[(x,y,z)]==g.TRAY for x in range(x0,x1+1)))
        self.assertEqual(g.manifest(self.m)['source_claims']['installed_cooking_bays'],2)

    def test_visual_slope_is_one_to_one_not_real_measurement(self):
        for z in range(8,24):
            self.assertEqual(g.slope(z)-g.slope(z+1),1)
        self.assertIn('arbitrary',g.manifest(self.m)['interpretation']['voxel_scale'])

    def test_three_nonfunctional_heater_regions(self):
        for z in g.FLOOR_Z:
            y=g.slope(z)
            for x in (6,24,41):
                self.assertEqual(self.m.blocks[(x,y+1,z)],g.HEATER)
            self.assertEqual(self.m.blocks[(23,y+1,z)],g.DIVIDER)
        self.assertFalse(g.manifest(self.m)['safety_and_truth']['thermal_simulation'])

    def test_guide_rods_four_per_bay(self):
        for z in (9,23):
            y=g.slope(z)
            for x in (10,16,30,36):
                self.assertEqual(self.m.blocks[(x,y+3,z)],g.ROD)

    def test_detached_trough_is_not_third_bay(self):
        for z in g.FLOOR_Z:
            self.assertEqual(self.m.blocks[(55,g.slope(z),z)],g.SPARE)
        self.assertIn('NOT third',g.manifest(self.m)['interpretation']['detached_sample'])

    def test_no_unexpected_overlaps(self):
        self.assertEqual(self.m.conflicts,[])
        self.assertGreater(len(self.m.blocks),2000)
        self.assertLess(len(self.m.blocks),4000)

    def test_build_only_uses_non_clobbering_placement(self):
        lines=g.build_function(self.m).splitlines()
        commands=[x for x in lines if x and not x.startswith('#')]
        self.assertEqual(len(commands),len(self.m.blocks))
        self.assertTrue(all(x.startswith('setblock ~') and x.endswith(' keep') for x in commands))
        self.assertFalse(any('execute' in x or 'summon' in x for x in commands))

    def test_four_pressure_display_functions_change_four_cells_only(self):
        for mode in ['off','low','medium','high']:
            commands=[x for x in g.indicator_function(mode).splitlines() if x.startswith('setblock')]
            self.assertEqual(len(commands),4)
            self.assertTrue(all(x.endswith(' replace') for x in commands))
            self.assertTrue(all('~1 ~34' in x for x in commands))

    def test_source_integrity_provenance_but_not_physics(self):
        manifest=g.manifest(self.m)
        self.assertEqual(manifest['source']['commit'],'a15388ebf2391807559d7cfb334a15c9f3f57992')
        self.assertEqual(manifest['provenance_disposition'],'CONCEPT_ONLY_UNMEASURED_HOLD')
        self.assertTrue(all(val is False for val in manifest['safety_and_truth'].values()))
        self.assertEqual(len(manifest['next_real_measurements']),7)

    def test_datapack_contains_functions_and_manifest(self):
        package=g.make_datapack(self.m)
        with zipfile.ZipFile(io.BytesIO(package)) as z:
            paths=set(z.namelist())
            self.assertIn('pack.mcmeta',paths)
            for name in ('build','press_off','press_low','press_medium','press_high'):
                self.assertIn(f'data/nutoaster/function/{name}.mcfunction',paths)
            self.assertIn('SOURCE_CONCEPT.json',paths)
            pack=json.loads(z.read('pack.mcmeta'))
            self.assertEqual(pack['pack']['min_format'],[101,0])
            self.assertEqual(pack['pack']['max_format'],[101,0])
            self.assertEqual(json.loads(z.read('SOURCE_CONCEPT.json'))['voxel_count'],len(self.m.blocks))

    def test_legacy_java_1_20_1_format(self):
        package=g.make_datapack(self.m,'1.20.1')
        with zipfile.ZipFile(io.BytesIO(package)) as z:
            paths=set(z.namelist())
            self.assertIn('data/nutoaster/functions/build.mcfunction',paths)
            self.assertNotIn('data/nutoaster/function/build.mcfunction',paths)
            pack=json.loads(z.read('pack.mcmeta'))['pack']
            self.assertEqual(pack['pack_format'],15)
            self.assertNotIn('min_format',pack)
            self.assertEqual(json.loads(z.read('SOURCE_CONCEPT.json'))['minecraft_target'],'1.20.1')

    def test_unsupported_targets_refused(self):
        with self.assertRaises(AssertionError):g.make_datapack(self.m,'1.16.5')

    def test_reproducible_zip_bytes(self):
        self.assertEqual(g.make_datapack(self.m),g.make_datapack(g.build_model()))

if __name__=='__main__':unittest.main()
