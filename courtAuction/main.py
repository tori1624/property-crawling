from auction.auction_list import auction_list as run_list
from auction.auction_info import auction_info as run_info
import argparse


def main():
    parser = argparse.ArgumentParser(description="대법원 경매 크롤릴 실행")
    parser.add_argument(
        'mode', choices=['list', 'info'],
        help="list를 통해 경매 리스트를 크롤링한 이후, info를 통해 상세 정보 크롤링"
    )
    args = parser.parse_args()

    if args.mode == 'list':
        run_list()
    elif args.mode == 'info':
        run_info()

if __name__ == '__main__':
    main()
