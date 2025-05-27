import argparse

from .seeder import seed_url


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m ufvrag.seeder",
        description="Seed the starting point of the crawler with a URL.",
    )
    parser.add_argument(
        "--url",
        type=str,
        required=True,
        help="The URL to seed as the starting point for the crawler.",
    )
    args = parser.parse_args()

    seed_url(args.url)


if __name__ == "__main__":
    main()
