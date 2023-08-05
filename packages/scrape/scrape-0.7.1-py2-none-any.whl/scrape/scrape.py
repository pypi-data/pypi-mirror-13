#!/usr/bin/env python

######################################################################
#                                                                    #
# scrape - a command-line web scraping tool                          #
# written by Hunter Hammond (huntrar@gmail.com)                      #
#                                                                    #
######################################################################

from __future__ import absolute_import, print_function
import argparse as argp
import os
import sys

import lxml.html as lh
import pdfkit as pk

from scrape.orderedset import OrderedSet
from scrape import utils
from . import __version__


SYS_VERSION = sys.version_info[0]
if SYS_VERSION == 2:
    try:
        input = raw_input
    except NameError:
        pass

LINK_CACHE_SIZE = 100


def get_parser():
    """Parse command-line arguments"""
    parser = argp.ArgumentParser(
        description='a command-line web scraping tool')
    parser.add_argument('query', metavar='QUERY', type=str, nargs='*',
                        help='URL\'s/files to scrape')
    parser.add_argument('-a', '--attributes', type=str, nargs='*',
                        help='extract text using tag attributes')
    parser.add_argument('-c', '--crawl', type=str, nargs='*',
                        help='regexp rules for following new pages')
    parser.add_argument('-ca', '--crawl-all', help='crawl all pages',
                        action='store_true')
    parser.add_argument('-f', '--filter', type=str, nargs='*',
                        help='regexp rules for filtering text')
    parser.add_argument('-ht', '--html', help='write files as HTML',
                        action='store_true')
    parser.add_argument('-m', '--multiple', help='save to multiple files',
                        action='store_true')
    parser.add_argument('-mp', '--maxpages', type=int,
                        help='max number of pages to crawl')
    parser.add_argument('-ml', '--maxlinks', type=int,
                        help='max number of links to scrape')
    parser.add_argument('-n', '--nonstrict', action='store_true',
                        help='allow crawler to visit any domain')
    parser.add_argument('-o', '--out', type=str, nargs='*',
                        help='specify outfile names')
    parser.add_argument('-p', '--pdf', help='write files as pdf',
                        action='store_true')
    parser.add_argument('-q', '--quiet', help='suppress program output',
                        action='store_true')
    parser.add_argument('-s', '--single', help='save to a single file',
                        action='store_true')
    parser.add_argument('-t', '--text', help='write files as text (default)',
                        action='store_true')
    parser.add_argument('-v', '--version', help='display current version',
                        action='store_true')
    parser.add_argument('-x', '--xpath', type=str, nargs='?',
                        help='filter HTML using XPath')
    return parser


def follow_links(args, uncrawled_links, crawled_links, seed_url, seed_domain):
    """Follow links that have not been crawled yet

       Keyword arguments:
       args -- program arguments (dict)
       uncrawled_links -- links to be crawled (OrderedSet)
       crawled_links -- links already crawled (set)
       seed_url -- the first crawled link (str)
       seed_domain -- the domain of the seed URL (str)

       Retrieve HTML from links and write them to PART(#).html files.
    """
    crawled_ct = 1
    link_cache = []
    try:
        while uncrawled_links:
            # Check limit on number of links and pages to crawl
            if ((args['maxlinks'] and
                 len(crawled_links) >= args['maxlinks']) or
                    (args['maxpages'] and crawled_ct >= args['maxpages'])):
                break

            url = uncrawled_links.pop(last=False)
            # Compare scheme-less URLs to prevent http(s):// dupes
            if (utils.check_scheme(url) and
                    utils.remove_scheme(url) not in crawled_links):
                raw_html = utils.get_raw_html(url)
                if raw_html is not None:
                    html = lh.fromstring(raw_html)
                    # Compute a hash of the page and check if it is in cache
                    page_text = utils.parse_text(html)
                    link_hash = utils.hash_text(''.join(page_text))
                    if link_hash in link_cache:
                        continue
                    utils.cache_link(link_cache, link_hash, LINK_CACHE_SIZE)

                    # Find new links and remove fragments/append base url
                    # if necessary
                    links = [utils.clean_url(u, seed_url) for u in
                             html.xpath('//a/@href')]
                    crawled_ct += 1
                    # Domain may be restricted to the seed domain
                    if not args['nonstrict'] and seed_domain in url:
                        links = [x for x in links if seed_domain in x]
                    # Links may be filtered by regex keywords
                    if args['crawl']:
                        links = utils.re_filter(links, args['crawl'])

                    uncrawled_links.update(links)
                    crawled_links.add(utils.remove_scheme(url))
                    utils.write_part_file(args, raw_html, len(crawled_links))
                    if not args['quiet']:
                        print('Crawled {0} (#{1}).'
                              .format(url, len(crawled_links)))
                else:
                    if not args['quiet']:
                        sys.stderr.write('Failed to parse {0}.\n'
                                         .format(url))
    except (KeyboardInterrupt, EOFError):
        pass


def crawl(args, seed_url, seed_domain):
    """Find links given a seed URL and follow them breadth-first

       Keyword arguments:
       args -- program arguments (dict)
       seed_url -- the first link to crawl (str)
       seed_domain -- the domain of the seed URL (str)

       Initialize crawled/uncrawled links by exctracting links from a seed URL.
       Returns the PART.html filenames created during crawling.
    """
    prev_part_num = utils.get_num_part_files()
    crawled_links = set()
    uncrawled_links = OrderedSet()
    raw_html = utils.get_raw_html(seed_url)
    if raw_html is not None:
        html = lh.fromstring(raw_html)
        # Find new links and remove fragments/append base url if necessary
        links = [utils.clean_url(u, seed_url) for u
                 in html.xpath('//a/@href')]
        # Domain may be restricted to the seed domain
        if not args['nonstrict']:
            links = [x for x in links if seed_domain in x]
        # Links may be filtered by regex keywords
        if args['crawl']:
            for keyword in args['crawl']:
                links = [x for x in links if keyword in x]

        uncrawled_links.update(links)
        crawled_links.add(utils.remove_scheme(seed_url))
        utils.write_part_file(args, raw_html, len(crawled_links))
        if not args['quiet']:
            print('Crawled {0} (#{1}).'.format(seed_url, len(crawled_links)))
        follow_links(args, uncrawled_links, crawled_links, seed_url,
                     seed_domain)
    curr_part_num = utils.get_num_part_files()
    return utils.get_part_filenames(curr_part_num, prev_part_num)


def pdfkit_convert_xpath(args, infilenames, outfilenames, options):
    """Filter HTML files by XPath and then convert to PDF using pdfkit

       Keyword arguments:
       args -- program arguments (dict)
       infilenames -- names of input files (list)
       outfilenames -- names of output PDF files (list)
       options -- pdfkit options (dict)
    """
    if args['multiple']:
        html = None
        for i, infilename in enumerate(infilenames):
            if not args['quiet']:
                print('Attempting to write to {0}.'
                      .format(outfilenames[i]))
            else:
                options['quiet'] = None

            html = utils.parse_html(utils.read_files(infilename),
                                    args['xpath'])
            if isinstance(html, list):
                if isinstance(html[0], str):
                    pk.from_string('\n'.join(html), outfilenames[i],
                                   options=options)
                else:
                    pk.from_string('\n'.join(lh.tostring(x) for x in html),
                                   outfilenames[i], options=options)
            elif isinstance(html, str):
                pk.from_string(html, outfilenames[i], options=options)
            else:
                pk.from_string(lh.tostring(html), outfilenames[i],
                               options=options)
    elif args['single']:
        if not args['quiet']:
            print('Attempting to write {0} page(s) to {1}.'
                  .format(len(infilenames), outfilenames[0]))
        else:
            options['quiet'] = None

        html = utils.parse_html(utils.read_files(infilenames),
                                args['xpath'])
        if isinstance(html, list):
            if isinstance(html[0], str):
                pk.from_string('\n'.join(html), outfilenames[0],
                               options=options)
            else:
                pk.from_string('\n'.join(lh.tostring(x) for x in html),
                               outfilenames[0], options=options)
        elif isinstance(html, str):
            pk.from_string(html, outfilenames[0], options=options)
        else:
            pk.from_string(lh.tostring(html), outfilenames[0],
                           options=options)


def pdfkit_convert(args, infilenames, outfilenames):
    """Convert files to PDF using pdfkit

       Keyword arguments:
       args -- program arguments (dict)
       infilenames -- names of input files (list)
       outfilenames -- names of output PDF files (list)
    """
    options = {}
    # Only ignore errors if there is more than one page
    # This prevents an empty write if an error occurs
    if len(infilenames) > 1:
        options['ignore-load-errors'] = None

    try:
        if args['xpath']:
            pdfkit_convert_xpath(args, infilenames, outfilenames, options)
        elif args['multiple']:
            for i, infilename in enumerate(infilenames):
                if not args['quiet']:
                    print('Attempting to write to {0}.'
                          .format(outfilenames[i]))
                else:
                    options['quiet'] = None
                pk.from_file(infilename, outfilenames[i], options=options)
        elif args['single']:
            if not args['quiet']:
                print('Attempting to write {0} page(s) to {1}.'
                      .format(len(infilenames), outfilenames[0]))
            else:
                options['quiet'] = None
            pk.from_file(infilenames, outfilenames[0], options=options)
    except (KeyboardInterrupt, Exception):
        if args['urls']:
            utils.remove_part_files()
        raise


def write_to_pdf(args, infilenames, outfilenames):
    """Write files to PDF

       Keyword arguments:
       args -- program arguments (dict)
       infilenames -- names of input files (list)
       outfilenames -- names of output PDF files (list)

       Convert files to PDF using pdfkit.
    """
    if args['multiple']:
        pdf_filenames = [x + '.pdf' for x in outfilenames]
        outfilenames = pdf_filenames
        for filename in outfilenames:
            utils.remove_file(filename)
        pdfkit_convert(args, infilenames, outfilenames)
    elif args['single']:
        outfilename = outfilenames[0] + '.pdf'
        utils.remove_file(outfilename)
        pdfkit_convert(args, infilenames, [outfilename])


def write_to_text(args, infilenames, outfilenames):
    """Write files to text

       Keyword arguments:
       args -- program arguments (dict)
       infilenames -- names of input files (list)
       outfilenames -- names of output text files (list)

       Text is parsed using XPath, regexes, or tag attributes prior to writing.
    """
    if args['multiple']:
        # Write input files to multiple text files
        txt_filenames = [x + '.txt' for x in outfilenames]
        outfilenames = txt_filenames
    elif args['single']:
        # Aggregate all text for writing to a single output file
        all_text = []

    for i, infilename in enumerate(infilenames):
        if infilename.endswith('.html'):
            # Convert HTML to lxml object for content parsing
            html = lh.fromstring(utils.read_files(infilename))
            text = None
        else:
            html = None
            text = utils.read_files(infilename)

        if html is not None:
            parsed_text = utils.parse_text(html, args['xpath'], args['filter'],
                                           args['attributes'])
        elif text is not None:
            parsed_text = utils.parse_text(text, args['xpath'], args['filter'])
        else:
            if not args['quiet']:
                if args['files']:
                    sys.stderr.write('Failed to parse file {0}.\n'
                                     .format(outfilenames[i].replace(
                                         '.txt', '.html')))
                else:
                    sys.stderr.write('Failed to parse PART{0}.html.\n'
                                     .format(i + 1))

        if parsed_text:
            if args['multiple']:
                if not args['quiet']:
                    print('Attempting to write to {0}.'
                          .format(outfilenames[i]))
                utils.remove_file(outfilenames[i])
                utils.write_file(parsed_text, outfilenames[i])
            elif args['single']:
                all_text += parsed_text
                # Newline added between multiple files being aggregated
                if len(infilenames) > 1 and i < len(infilenames) - 1:
                    all_text.append('\n')

    # Write all text to a single output file
    if args['single'] and all_text:
        outfilename = outfilenames[0] + '.txt'
        if not args['quiet']:
            print('Attempting to write {0} page(s) to {1}.'
                  .format(len(infilenames), outfilename))
        utils.remove_file(outfilename)
        utils.write_file(all_text, outfilename)


def write_files(args, infilenames, outfilenames):
    """Write scraped or local files to text or PDF
    
       Keyword arguments:
       args -- program arguments (dict)
       infilenames -- names of user-inputted files (list)
       outfilenames -- names of output PDF files (list)
       filetypes -- types of files in infilenames (list)

       File types are 'files' for local files, or 'urls' for scraped files.
       Remove PART(#).html files after conversion unless otherwise specified.
       """
    if args['pdf']:
        write_to_pdf(args, infilenames, outfilenames)
    elif args['text']:
        write_to_text(args, infilenames, outfilenames)
    if args['urls'] and not args['html']:
        utils.remove_part_files()


def get_single_outfilename(args):
    """Use first possible entry in query as filename"""
    for arg in args['query']:
        if arg in args['files']:
            return ('.'.join(arg.split('.')[:-1])).lower()
        for url in args['urls']:
            if arg.strip('/') in url:
                domain = utils.get_domain(url)
                return utils.get_outfilename(url, domain)
    sys.stderr.write('Failed to construct a single out filename.\n')
    return ''


def write_single_file(args, base_dir):
    """Write to a single output file and/or subdirectory"""
    infilenames = []
    if args['urls']:
        domain = args['domains'][0]
        if args['html']:
            # Create a single directory to store HTML files in
            if not args['quiet']:
                print('Storing html files in {0}/'.format(domain))
            utils.mkdir_and_cd(domain)

    for query in args['query']:
        if query.strip('/') in args['urls']:
            if args['crawl'] or args['crawl_all']:
                # crawl traverses and saves pages as PART.html files
                infilenames += crawl(args, query, domain)
            else:
                raw_html = utils.get_raw_html(query)
                if raw_html is not None:
                    prev_part_num = utils.get_num_part_files()
                    utils.write_part_file(args, raw_html)
                    curr_part_num = utils.get_num_part_files()
                    infilenames += utils.get_part_filenames(curr_part_num,
                                                            prev_part_num)
                else:
                    return False
        elif query in args['files']:
            infilenames.append(query)

    if args['html']:
        # HTML files have been written already, so return to base directory
        os.chdir(base_dir)
    else:
        # Write files to text or pdf
        if args['out']:
            outfilename = args['out'][0]
        else:
            outfilename = get_single_outfilename(args)
        if outfilename:
            write_files(args, infilenames, [outfilename])
        else:
            utils.remove_part_files()
    return True


def write_multiple_files(args, base_dir):
    """Write to multiple output files and/or subdirectories"""
    urls_ct = 0
    for i, query in enumerate(args['query']):
        if query in args['files']:
            # Write files
            if args['out'] and i < len(args['out']):
                outfilename = args['out'][i]
            else:
                outfilename = '.'.join(query.split('.')[:-1])
            write_files(args, [query], [outfilename])
        elif query in args['urls']:
            # Scrape/crawl urls
            domain = args['domains'][urls_ct]
            urls_ct += 1
            if args['html']:
                # Save .html files in a subdir named after the domain
                if not args['quiet']:
                    print('Storing html files in {0}/'.format(domain))
                utils.mkdir_and_cd(domain)

            # Crawl and/or write HTML files to disk
            if args['crawl'] or args['crawl_all']:
                # Traverses and saves pages as PART.html files
                prev_part_num = utils.get_num_part_files()
                crawl(args, query, domain)
                curr_part_num = utils.get_num_part_files()
            else:
                raw_html = utils.get_raw_html(query)
                if raw_html is not None:
                    # Saves page as PART.html file
                    prev_part_num = utils.get_num_part_files()
                    utils.write_part_file(args, raw_html)
                    curr_part_num = prev_part_num + 1
                else:
                    return False

            if args['html']:
                # HTML files have been written already, so return to base directory
                os.chdir(base_dir)
            else:
                # Write files to text or pdf
                infilenames = utils.get_part_filenames(curr_part_num,
                                                           prev_part_num)
                if args['out'] and i < len(args['out']):
                    outfilename = args['out'][i]
                else:
                    outfilename = utils.get_outfilename(query, domain)
                write_files(args, infilenames, [outfilename])
    return True


def scrape(args):
    """Extract, filter, and convert webpages to text, pdf, or HTML files"""
    try:
        base_dir = os.getcwd()

        if args['out'] is None:
            args['out'] = []

        # Detect whether to save to a single or multiple files
        if not args['single'] and not args['multiple']:
            # Save to multiple files if multiple files/URL's entered
            if len(args['query']) > 1 or len(args['out']) > 1:
                args['multiple'] = True
            else:
                args['single'] = True

        # Split query input into local files and URL's
        args['files'] = []
        args['urls'] = []
        for arg in args['query']:
            if os.path.isfile(arg):
                args['files'].append(arg)
            else:
                args['urls'].append(arg.strip('/'))

        # Print error if attempting to convert local files to HTML
        if args['files'] and args['html']:
            sys.stderr.write('Cannot convert local files to HTML.\n')
            args['files'] = []

        if args['urls']:
            # Add URL extensions and schemes
            urls_with_exts = [utils.add_url_ext(x) for x in args['urls']]
            args['urls'] = [utils.add_scheme(x) if not utils.check_scheme(x)
                            else x for x in urls_with_exts]
            args['domains'] = [utils.get_domain(x) for x in args['urls']]
        else:
            args['domains'] = []

        if args['single']:
            return write_single_file(args, base_dir)
        elif args['multiple']:
            return write_multiple_files(args, base_dir)
    except (KeyboardInterrupt, Exception):
        if args['html']:
            try:
                os.chdir(base_dir)
            except OSError:
                pass
        else:
            utils.remove_part_files()
        raise


def command_line_runner():
    """Handle command-line interaction"""
    parser = get_parser()
    args = vars(parser.parse_args())
    if args['version']:
        print(__version__)
        return
    if not args['query']:
        parser.print_help()
        return

    if not args['text'] and not args['pdf'] and not args['html']:
        valid_types = ['text', 'pdf', 'html']
        try:
            filetype = input('Save output as ({0}): '
                             .format(', '.join(valid_types))).lower()
            while filetype not in valid_types:
                filetype = input('Invalid entry. Choose from ({0}): '
                                 .format(', '.join(valid_types))).lower()
        except (KeyboardInterrupt, EOFError):
            return
        args[filetype] = True
    scrape(args)


if __name__ == '__main__':
    command_line_runner()
