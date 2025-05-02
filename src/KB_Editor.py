
import pandas as pd
import argparse
import sys

KB_PATH = r"C:\Users\Sab3awy\Knowledge-Based-System-for-AIU-Course-Registration-Advising\data\courses.csv"

def load_kb():
    return pd.read_csv(KB_PATH, dtype=str).fillna('')

def save_kb(df):
    df.to_csv(KB_PATH, index=False)
    print(f"KB updated: {KB_PATH}")

def list_courses(args):
    df = load_kb()
    if args.code:
        df = df[df['Course Code'] == args.code]
    print(df.to_markdown(index=False))

def add_course(args):
    df = load_kb()
    if args.code in df['Course Code'].values:
        print(f"Error: Course {args.code} already exists.", file=sys.stderr)
        sys.exit(1)
    new = {
        'Course Code': args.code,
        'Course Name': args.name,
        'Prerequisites': args.prereqs or '',
        'Co-requisites': args.coreqs or '',
        'Credit Hours': args.credits,
        'Semester Offered': args.semester,
        'Track': args.track,
        'Level': args.level,
        'Description': args.description or ''
    }
    df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
    save_kb(df)

def edit_course(args):
    df = load_kb()
    idx = df.index[df['Course Code'] == args.code]
    if len(idx) == 0:
        print(f"Error: Course {args.code} not found.", file=sys.stderr)
        sys.exit(1)
    i = idx[0]
    for field, val in {
        'Course Name': args.name,
        'Prerequisites': args.reprereqs,
        'Co-requisites': args.recoreqs,
        'Credit Hours': args.credits,
        'Semester Offered': args.semester,
        'Track': args.track,
        'Level': args.level,
        'Description': args.description
    }.items():
        if val is not None:
            df.at[i, field] = val
    save_kb(df)

def delete_course(args):
    df = load_kb()
    if args.code not in df['Course Code'].values:
        print(f"Error: Course {args.code} not found.", file=sys.stderr)
        sys.exit(1)
    df = df[df['Course Code'] != args.code]
    save_kb(df)

def main():
    p = argparse.ArgumentParser(description="KB Editor for courses_kb.csv")
    sub = p.add_subparsers(dest='cmd', required=True)

    # list
    p_list = sub.add_parser('list', help='List all or one course')
    p_list.add_argument('-c','--code', help='Course Code to filter')
    p_list.set_defaults(func=list_courses)

    # add
    p_add = sub.add_parser('add', help='Add a new course')
    p_add.add_argument('code')
    p_add.add_argument('name')
    p_add.add_argument('--prereqs', help='Comma-sep prereqs')
    p_add.add_argument('--coreqs', help='Comma-sep coreqs')
    p_add.add_argument('--credits', type=int, required=True)
    p_add.add_argument('--semester', choices=['Fall','Spring','Both'], required=True)
    p_add.add_argument('--track', default='All')
    p_add.add_argument('--level', type=int, required=True)
    p_add.add_argument('--description', help='Short course summary')
    p_add.set_defaults(func=add_course)

    # edit
    p_edit = sub.add_parser('edit', help='Edit an existing course')
    p_edit.add_argument('code')
    p_edit.add_argument('--name')
    p_edit.add_argument('--reprereqs', help='New comma-sep prereqs')
    p_edit.add_argument('--recoreqs', help='New comma-sep coreqs')
    p_edit.add_argument('--credits', type=int)
    p_edit.add_argument('--semester', choices=['Fall','Spring','Both'])
    p_edit.add_argument('--track')
    p_edit.add_argument('--level', type=int)
    p_edit.add_argument('--description')
    p_edit.set_defaults(func=edit_course)

    # delete
    p_del = sub.add_parser('delete', help='Remove a course')
    p_del.add_argument('code')
    p_del.set_defaults(func=delete_course)

    args = p.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
