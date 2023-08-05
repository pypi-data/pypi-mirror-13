from .latex import format_tokens as format_latex_tokens
from .main import Fountain
import argparse

def to_latex():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=argparse.FileType('r'), default='-')
    args = parser.parse_args()
    fountain = Fountain()
    print(format_latex_tokens(fountain.tokenize(args.input.readlines())))
