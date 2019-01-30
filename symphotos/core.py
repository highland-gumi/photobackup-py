from gui import window
import argparse
from action.archive import Archive as Archive
from photo_util.common_utils import DateUtil

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--archive', action='store_true')
    parser.add_argument('-m', '--month')
    args = parser.parse_args()

    if args.archive:
        arch_month = args.month if args.month else None
        to_date = DateUtil.default_from_day(arch_month=arch_month)
        Archive(to_date=to_date).func_exec_by_date()
    else:
        window.Top().create_window()
