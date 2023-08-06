# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- YAML based data loader
# :Created:   ven 01 gen 2016 16:33:36 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: Copyright (C) 2016 Lele Gaifax
#

from logging import getLogger
import os.path
import sys

import pkg_resources

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from . import load


logger = getLogger(__name__)

OK, LOAD_ERROR, LOAD_EXCEPTION, PRELOAD_EXCEPTION, POSTLOAD_EXCEPTION = range(5)

def workhorse(uri, dry_run, echo, delete, save_new_instances, preload, postload, fnames):
    "Load one or more YAML file into the database."

    engine = create_engine(uri, echo=echo)
    salogger = getattr(engine.logger, 'logger', None)
    if salogger is not None:
        for h in salogger.handlers:
            salogger.removeHandler(h)
    smaker = sessionmaker(autoflush=False, autocommit=False, bind=engine)

    session = smaker()

    if preload is not None:
        try:
            f = open(preload)
        except IOError:
            logger.error(u"Could not open preload script %r!" % preload)
            return PRELOAD_EXCEPTION

        logger.debug('Executing preload script %r...', preload)
        context = dict(session=session, dry_run=dry_run, fnames=fnames)
        try:
            code = compile(f.read(), preload, 'exec')
            exec(code, context)
            fnames = context['fnames']
        except Exception:
            logger.exception(u"Failure executing the preload script!")
            return PRELOAD_EXCEPTION
        finally:
            f.close()

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
        return LOAD_ERROR
    except Exception:
        logger.exception(u"We are in trouble, unexpected error!")
        return LOAD_EXCEPTION

    if postload is not None:
        try:
            f = open(postload)
        except IOError:
            logger.error(u"Could not open postload script %r!" % postload)
            return POSTLOAD_EXCEPTION

        logger.debug('Executing postload script %r...', postload)
        context = dict(session=session, dry_run=dry_run, fnames=fnames)
        try:
            code = compile(f.read(), postload, 'exec')
            exec(code, context)
        except Exception:
            logger.exception(u"Failure executing the postload script!")
            return POSTLOAD_EXCEPTION
        finally:
            f.close()

    if not dry_run:
        logger.info(u"Committing changes")
        session.commit()

    return OK


def path_spec(ps):
    if os.path.isabs(ps) or not ':' in ps:
        return ps
    pkgname, subpath = ps.split(':', 1)
    return pkg_resources.resource_filename(pkgname, subpath)


def main():
    import locale, logging
    from argparse import ArgumentParser, RawDescriptionHelpFormatter

    locale.setlocale(locale.LC_ALL, '')

    parser = ArgumentParser(
        description="Load and/or update DB model instances.",
        epilog=__doc__, formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument("datafile", nargs="+", type=path_spec,
                        help=u"The YAML data file to load. It may be either a plain"
                        " file name, or a package relative path like"
                        " “package.name:some/file”.")
    parser.add_argument("-u", "--sqlalchemy-uri", type=str, metavar="URI",
                        help=u"Specify the SQLAlchemy URI.", default=None)
    parser.add_argument("-D", "--delete", default=False, action="store_true",
                        help="Delete existing instances instead of creating/"
                        "updating them. You better know what you are doing!")
    parser.add_argument("-s", "--save-new-instances", type=str, metavar='FILE',
                        help=u"Save new instances information into given YAML file,"
                        " preserving it's previous content.")
    parser.add_argument("-p", "--preload", type=path_spec, metavar='SCRIPT',
                        help=u"Execute the given Python script before loading the"
                        " data files. It may be either a plain file name or a package"
                        " relative path like “package.name:some/file”.")
    parser.add_argument("-P", "--postload", type=path_spec, metavar='SCRIPT',
                        help=u"Execute the given Python script after load but before"
                        " committing changes. It may be either a plain file name or a"
                        " package relative path like"
                        " “package.name:some/file”.")
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
                     args.delete, args.save_new_instances,
                     args.preload, args.postload, args.datafile)


if __name__ == '__main__':
    sys.exit(main())
