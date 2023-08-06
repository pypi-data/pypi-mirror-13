import sys
import logging

from pprint import pprint as pp
from datetime import datetime
import click

from gemini import GeminiQuery


def check_genotypes(gemini_variant, index):
    """Check the genotypes for a variant"""
    print(gemini_variant['gts'][index])
    print(gemini_variant['gt_types'][index])

@click.command()
@click.argument('db',
    type=click.Path(exists=True),
    # type=click.Path(exists=True),
)
@click.option('-v', '--variant',
    type=int
)
@click.option('--value',
)
@click.option('--query',
    default="SELECT * from variants"
)
def test_gemini(db, variant, value, query):
    """Test a gemini db"""
    gq = GeminiQuery(db)
    
    # query = "SELECT * from variant_impacts WHERE variant_id = 1"
    # query = "SELECT * from samples"
    
    # query = "gemini comp_hets"
    
    # if variant:
    #     query = "SELECT * from variants WHERE (aaf_1kg_all < {0} or aaf_1kg_all is Null)".format(variant)
    # else:
    #      query = "select * from variants"
    
    # query = "SELECT * from variants WHERE impact_severity in ('HIGH', 'LOW')"
    gq.run(query)
    sample2idx = gq.sample_to_idx
    
    for index, variant in enumerate(gq):
        for key in variant.keys():
            if value:
                if key == value:
                    print("{0}: {1}".format(key, variant[key]))
            else:
                print("'{0}': {1},".format(key, variant[key]))
        print("")
        # check_genotypes(variant, 0)
        # check_genotypes(variant, 1)
        # check_genotypes(variant, 2)
    
    print(sample2idx)
    print(index)


if __name__ == '__main__':
    test_gemini()
