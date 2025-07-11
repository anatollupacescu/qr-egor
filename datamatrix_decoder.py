import os
from pdf2image import convert_from_path
import cv2
from pylibdmtx.pylibdmtx import decode
import csv
import numpy
import sys
import argparse

def enhance_image(image):
    """Enhance image for better Data Matrix detection"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 51, 7
    )
    return thresh

def process_pdf_codes(pdf_path):
    try:
        if not os.path.exists(pdf_path):
            print(f"PDF file not found: {pdf_path}", file=sys.stderr)
            return False

        pages = convert_from_path(pdf_path)

        # Set up CSV writer for stdout
        writer = csv.writer(sys.stdout)
        writer.writerow(['Page', 'Content'])

        codes_found = 0
        for page_num, page in enumerate(pages, 1):
            opencv_image = cv2.cvtColor(numpy.array(page), cv2.COLOR_RGB2BGR)
            enhanced_image = enhance_image(opencv_image)
            codes = decode(enhanced_image)

            for code in codes:
                try:
                    content = code.data.decode('utf-8').strip()
                    writer.writerow([page_num, content])
                    codes_found += 1
                except Exception as e:
                    print(f"Error decoding Data Matrix on page {page_num}: {str(e)}", file=sys.stderr)
                    return False

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
