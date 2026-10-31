"""Vectores publicos del perfil determinista GISELA v1."""
import copy
from decimal import Decimal
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from canonical import canonical_json, package_digest, CanonicalError
from rng import RNGState, draw, MAX_COUNTER
from admit_package import admit_package, PackageRejected
from semantic_validator import Validator

HERE = Path(__file__).parent

class CanonicalVectors(unittest.TestCase):
    def test_order_and_spaces_are_irrelevant(self):
        a=json.loads('{"b": 2, "a": 1}')
        b=json.loads('{"a":1,"b":2}')
        self.assertEqual(canonical_json(a),b'{"a":1,"b":2}')
        self.assertEqual(package_digest(a),'71f9517491c6e88f57079c8863c0a9d743df687ec07f4eb60a375b85fb14d85e')
        self.assertEqual(package_digest(a),package_digest(b))

    def test_unicode(self):
        data={'café':'niño','a':[3,True,None]}
        self.assertEqual(canonical_json(data),'{"a":[3,true,null],"café":"niño"}'.encode())
        self.assertEqual(package_digest(data),'a258243abed9942bc6cb6be2d27bec588d0a4b8a2b4792419181df11570f50fb')

    def test_decimals_preserve_exact_value(self):
        a={'v':Decimal('0.1000'),'u':Decimal('1.00')}
        self.assertEqual(canonical_json(a),b'{"u":1,"v":0.1}')
        self.assertEqual(canonical_json(a),canonical_json({'u':1,'v':Decimal('0.1')}))
        self.assertEqual(package_digest(a),'b3cc881308865f2399929106b8e13f495546ca8d354e08b78698142220adea86')

    def test_array_order_is_meaningful(self):
        self.assertNotEqual(package_digest({'list':[1,2]}),package_digest({'list':[2,1]}))

    def test_negative_zero_and_small_decimal(self):
        self.assertEqual(canonical_json({'a':Decimal('-0.0'),'b':Decimal('0.0000001')}),b'{"a":0,"b":0.0000001}')

    def test_bad_json_values(self):
        for value in [float('nan'), float('inf'), {1:'a'}, {'bad':'\ud800'}, 9007199254740992, Decimal('1e6000')]:
            with self.subTest(value=str(value)[:50]), self.assertRaises(CanonicalError):canonical_json(value)

    def test_admission_digest_and_mutation(self):
        p=json.loads((HERE/'example.package.json').read_text())
        accepted=admit_package(p)
        self.assertEqual(accepted.digest,'f6ffaf227c512a4aa10510703811f9f18539521a288ea57959350c648d81cabb')
        p['manifest']['id']='other'
        self.assertNotEqual(package_digest(p),accepted.digest)
        self.assertEqual(accepted.materialize()['manifest']['id'],'central_clasificadora_fixture')

    def test_snapshot_digest_checked(self):
        p=json.loads((HERE/'example.package.json').read_text())
        snap=json.loads((HERE/'semantic_examples/session_exploring_valid.json').read_text())
        self.assertNotIn('DIGEST_MISMATCH',[d.code for d in Validator().validate_session(snap,p)])
        snap['package_digest']='0'*64
        self.assertIn('DIGEST_MISMATCH',[d.code for d in Validator().validate_session(snap,p)])

class RNGVectors(unittest.TestCase):
    def test_zero_seed_vectors(self):
        for sides,expected in [(1,1),(2,2),(6,6),(10,6),(100,76),(1000003,523749)]:
            with self.subTest(sides=sides):
                got,new=draw(RNGState('00'*32),sides)
                self.assertEqual((got,new.counter),(expected,1))

    def test_second_seed(self):
        for sides,expected in [(1,1),(2,2),(6,4),(10,10),(100,100),(1000003,107399)]:
            with self.subTest(sides=sides):
                got,new=draw(RNGState('0123456789abcdef'*4),sides)
                self.assertEqual((got,new.counter),(expected,1))

    def test_immutability_and_replay(self):
        original=RNGState('00'*32)
        first,new=draw(original,6)
        second,after=draw(new,6)
        self.assertEqual(original.counter,0)
        self.assertEqual((first,second,after.counter),(6,draw(new,6)[0],2))
        self.assertEqual(draw(original,6),(first,new))

    def test_invalid_state_or_draw(self):
        with self.assertRaises(ValueError): RNGState('B'*64)
        with self.assertRaises(ValueError): draw(RNGState('00'*32),False)
        with self.assertRaises(ValueError): draw(RNGState('00'*32),0)
        with self.assertRaises(OverflowError): draw(RNGState('00'*32,MAX_COUNTER),6)

    def test_rejection_consumes_extra_block(self):
        class FakeDigest:
            def __init__(self,payload): self.payload=payload
            def digest(self):return (2**256-1 if self.payload.endswith((0).to_bytes(8,'big')) else 5).to_bytes(32,'big')
        with patch('rng.hashlib.sha256', side_effect=lambda data: FakeDigest(data)):
            val,new=draw(RNGState('00'*32),10)
            self.assertEqual((val,new.counter),(6,2))

if __name__=='__main__':unittest.main()

class PublishedVectors(unittest.TestCase):
    def test_published_digest_vectors(self):
        spec=json.loads((HERE.parents[1]/'docs/determinism/VECTORES.json').read_text())
        for case in spec['digest_vectors']:
            with self.subTest(name=case['name']):
                self.assertEqual(canonical_json(case['input']).decode(),case['canonical'])
                self.assertEqual(package_digest(case['input']),case['digest'])

    def test_published_rng_vectors(self):
        spec=json.loads((HERE.parents[1]/'docs/determinism/VECTORES.json').read_text())
        for case in spec['rng_vectors']:
            with self.subTest(seed=case['seed'][:8],sides=case['sides']):
                result,new=draw(RNGState(case['seed'],case['counter']),case['sides'])
                self.assertEqual((result,new.counter),(case['result'],case['next_counter']))
