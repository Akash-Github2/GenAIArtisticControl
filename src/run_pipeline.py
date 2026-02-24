import sys
import argparse
sys.path.append('src')

from pipelines import run_code_blend, run_oneshot, run_llm_blend


def add_coord_args(subparser):
    subparser.add_argument("image_name")
    subparser.add_argument("session_name")
    subparser.add_argument("prompt")
    subparser.add_argument("--x1", type=int, required=True)
    subparser.add_argument("--y1", type=int, required=True)
    subparser.add_argument("--x2", type=int, required=True)
    subparser.add_argument("--y2", type=int, required=True)
    subparser.add_argument("--padding", type=int, required=True)


def main():
    parser = argparse.ArgumentParser(description="Run image editing pipelines")
    subs = parser.add_subparsers(dest="method", required=True)

    # code-blend
    add_coord_args(subs.add_parser("code-blend"))

    # oneshot
    oneshot = subs.add_parser("oneshot")
    oneshot.add_argument("image_name")
    oneshot.add_argument("session_name")
    oneshot.add_argument("prompt")

    # llm-blend
    add_coord_args(subs.add_parser("llm-blend"))

    args = parser.parse_args()

    if args.method == "code-blend":
        run_code_blend(args.image_name, args.session_name, args.prompt,
                       args.x1, args.y1, args.x2, args.y2, args.padding)
    elif args.method == "oneshot":
        run_oneshot(args.image_name, args.session_name, args.prompt)
    elif args.method == "llm-blend":
        run_llm_blend(args.image_name, args.session_name, args.prompt,
                      args.x1, args.y1, args.x2, args.y2, args.padding)


if __name__ == "__main__":
    main()
