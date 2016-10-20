import argparse
from . import Skeleton, SkelMotion, Pose


def plot(args):
    sk = Skeleton(args.skeleton, scale=float(args.scale))
    skm = SkelMotion(sk, args.motion, (1.0 / float(args.framerate)))
    p = Pose(sk, skm)
    p.plot(0, -1)


def main():
    parser = argparse.ArgumentParser(description='View/parse asf/amc files.')
    parser.add_argument('--sk', dest='skeleton', required=True,
                        help='Path to *.asf file')
    parser.add_argument('--motion', dest='motion', required=True,
                        help='Path to *.amc file')
    parser.add_argument('--scale', default=1.0, required=False)
    parser.add_argument('--framerate', default=120.0)
    args = parser.parse_args()

    plot(args)


if __name__ == "__main__":
    main()
