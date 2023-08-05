# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- YAML based data loader
# :Created:   ven 01 gen 2016 16:33:36 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: Copyright (C) 2016 Lele Gaifax
#

from logging import getLogger
import sys

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from . import load


logger = getLogger(__name__)


def workhorse(uri, dry_run, echo, delete, save_new_instances, fnames):
    "Load one or more YAML file into the database."

    engine = create_engine(uri, echo=echo)
    salogger = getattr(engine.logger, 'logger', None)
    if salogger is not None:
        for h in salogger.handlers:
            salogger.removeHandler(h)
    smaker = sessionmaker(autoflush=False, autocommit=False, bind=engine)

    session = smaker()

    try:
        for fname in fnames:
            load(fname, session, dry_run, delete, save_new_instances,
                 show_progress=not echo)
    except SQLAlchemyError as e:
        # PG errors are UTF-8 encoded
        emsg = str(e)
        if sys.version_info.major < 3:
            emsg = emsg.decode('utf-8')
        logger.error(u"Data couldn't be loaded: %s", emsg)
        return 1
    except Exception:
        logger.exception(u"We are in trouble, unexpected error!")
        return 2
    else:
        if not dry_run:
            logger.info(u"Committing changes")
            session.commit()

    return 0 # OK


def main():
    import locale, logging
    from argparse import ArgumentParser, RawDescriptionHelpFormatter

    locale.setlocale(locale.LC_ALL, '')

    parser = ArgumentParser(
        description="Load and/or update DB model instances.",
        epilog=__doc__, formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument("datafile", nargs="+",
                        help=u"The YAML data file to load.")
    parser.add_argument("-u", "--sqlalchemy-uri", type=str, metavar="URI",
                        help=u"Specify the SQLAlchemy URI.", default=None)
    parser.add_argument("-D", "--delete", default=False, action="store_true",
                        help="Delete existing instances instead of creating/"
                        "updating them. You better know what you are doing!")
    parser.add_argument("-s", "--save-new-instances", type=str, metavar='FILE',
                        help=u"Save new instances information into given YAML file,"
                        " preserving it's previous content.")
    parser.add_argument("-n", "--dry-run", default=False, action="store_true",
                        help=u"Don't commit the changes to the database.")
    parser.add_argument("-e", "--echo", default=False, action="store_true",
                        help=u"Activate SA engine echo")
    parser.add_argument("-d", "--debug", default=False, action="store_true",
                        help=u"Activate debug logging")
    if sys.version_info.major < 3:
        parser.add_argument("-w", "--unicode-warnings", default=False,
                            action="store_true",
                            help=u"Activate SA unicode warnings")

    args = parser.parse_args()

    logging.basicConfig(format='%(message)s',
                        level=logging.DEBUG if args.debug else logging.INFO)

    if args.sqlalchemy_uri is None:
        print(u"You must specify the SQLAlchemy URI, example:")
        print(u"  python %s -u postgresql://localhost/dbname data.yaml"
              % sys.argv[0])

        return 128

    if sys.version_info.major < 3 and args.unicode_warnings:
        import warnings
        from sqlalchemy.exc import SAWarning

        warnings.filterwarnings(
            'ignore', category=SAWarning,
            message="Unicode type received non-unicode bind param value")

    return workhorse(args.sqlalchemy_uri, args.dry_run, args.echo,
                     args.delete, args.save_new_instances, args.datafile)


if __name__ == '__main__':
    sys.exit(main())
