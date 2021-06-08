import os, shutil
from xml.etree import ElementTree as ET
import cv2

# *** put in the path of image and xml folders here ***
image_folder_path = 'C:/Users/Roy/Desktop/NLP Project/LAREX/John Larex/for-roy-example-that-requires-readingorder/usca_paucar/cropped_images' # numeric filenames only
xml_folder_path = 'C:/Users/Roy/Desktop/NLP Project/LAREX/John Larex/for-roy-example-that-requires-readingorder/usca_paucar/xml_region_descriptions'
result_folder_path = 'C:/Users/Roy/Desktop/NLP Project/LAREX/John Larex/for-roy-example-that-requires-readingorder/usca_paucar/result_folder'

for files in os.listdir(result_folder_path):
    path = os.path.join(result_folder_path, files)
    try:
        shutil.rmtree(path)
    except OSError:
        os.remove(path)

image_no = 14  # start at fourteen rather than zero
xml_no = 14

# processing every image and its corresponding xml file
for filename in os.listdir(image_folder_path):
    if filename.endswith(".png"):

        # read all the images and its xml files
        img = cv2.imread(image_folder_path + '/' + str(image_no) + '.png')
        xml = xml_folder_path +'/' + str(xml_no) + '.xml'
        tree = ET.parse(xml)
        root = tree.getroot()
        image_part = 0

        # specify namespace from the xml file
        namespaces = {'doc': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15'}

        # cover the images with plain white spaces if there are any
        for image_tag in root.findall('doc:Page/doc:ImageRegion/doc:Coords', namespaces=namespaces):
            image_value = image_tag.get('points')

            # tokenized the x,y coordinates
            s = image_value.split(' ')
            s = [list(map(int, i.split(','))) for i in s]
            x = [i[0] for i in s]
            y = [i[1] for i in s]

            # find the max and min of x,y coords and form a rectangle image
            max_X, min_X = max(x), min(x)
            max_Y, min_Y = max(y), min(y)
            crop_img = img[min_Y:max_Y, min_X:max_X]

            # creat mask and cover the image
            mask = cv2.rectangle(img, (min_X - 5, min_Y), (max_X + 5, max_Y), (255, 255, 255), -1)
            result = cv2.bitwise_and(img, mask)
            img = result

        # make sure to use Reading Order Option
        for tag2 in root.findall('doc:Page/doc:ReadingOrder/doc:OrderedGroup/doc:RegionRefIndexed', namespaces=namespaces):
            order = tag2.get('regionRef')

            if order is not None:
                for tag1 in root.findall('doc:Page/doc:TextRegion', namespaces=namespaces):
                    if tag1.get('id') == order:
                        coords= tag1[0]
                        value = coords.get('points')

                        # tokenized the x,y coordinates
                        s = value.split(' ')
                        s = [list(map(int, i.split(','))) for i in s]
                        x = [i[0] for i in s]
                        y = [i[1] for i in s]

                        # find the max and min of x,y coords and form a rectangle image
                        max_X, min_X = max(x), min(x)
                        max_Y, min_Y = max(y), min(y)
                        crop_img = img[min_Y:max_Y, min_X:max_X]

                        # resize
                        # crop_img = cv2.resize(crop_img, None, fx=0.5, fy=0.5)

                        # clean out all the small images. Only save paragraphs
                        # JTH: how to check if this is appropriate for our application?
                        height, width, channels = crop_img.shape
                        # print(height, width)
                        # if height > 54 and width > 700:

                        # save the results
                        name = result_folder_path + '/page' + str(image_no) + '-part' + str(image_part) + '.jpg'
                        cv2.imwrite(name, crop_img)
                        image_part += 1

                        # show the final images
                        # cv2.imshow('page ' + str(image_no) + ' - part ' + str(image_part), crop_img)
                        # cv2.waitKey(0)
                        # cv2.destroyAllWindows()

        image_no += 1
        xml_no += 1
