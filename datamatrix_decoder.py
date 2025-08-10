import os
from pdf2image import convert_from_path
import cv2
from pylibdmtx.pylibdmtx import decode
import csv
import numpy
import sys
import argparse
import multiprocessing
from functools import partial

def enhance_image(image):
    """Enhance image for better Data Matrix detection"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 51, 7
    )
    return thresh

def process_single_page(page, page_num):
    """Process a single page and return the decoded contents"""
    results = []
    try:
        opencv_image = cv2.cvtColor(numpy.array(page), cv2.COLOR_RGB2BGR)
        enhanced_image = enhance_image(opencv_image)
        codes = decode(enhanced_image)

        for code in codes:
            try:
                content = code.data.decode('utf-8').strip()
                results.append(content)
            except Exception as e:
                print(f"Error decoding Data Matrix on page {page_num}: {str(e)}", file=sys.stderr)
                return None
        return results
    except Exception as e:
        print(f"Error processing page {page_num}: {str(e)}", file=sys.stderr)
        return None

def process_pdf_codes(pdf_path):
    try:
        if not os.path.exists(pdf_path):
            print(f"PDF file not found: {pdf_path}", file=sys.stderr)
            return False

        pages = convert_from_path(pdf_path)
        
        # Set up CSV writer for stdout
        writer = csv.writer(sys.stdout)
        
        # Set up multiprocessing pool with number of CPU cores
        num_cores = multiprocessing.cpu_count()
        pool = multiprocessing.Pool(processes=num_cores)
        
        # Create a partial function with fixed arguments
        process_page_with_num = partial(process_single_page)
        
        # Process pages in parallel
        results = pool.starmap(process_page_with_num, [(page, page_num) for page_num, page in enumerate(pages, 1)])
        
        # Close and join the pool
        pool.close()
        pool.join()
        
        # Check if any page processing failed
        if None in results:
            return False
        
        # Write all results to CSV
        for page_results in results:
            for content in page_results:
                writer.writerow([content])
        
        return True

    except Exception as e:
        print(f"An error occurred: {str(e)}", file=sys.stderr)
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process PDF file and extract Data Matrix codes.')
    parser.add_argument('pdf_path', help='Path to the PDF file')
    args = parser.parse_args()

    success = process_pdf_codes(args.pdf_path)
    sys.exit(0 if success else 1)
