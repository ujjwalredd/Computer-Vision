from PIL import Image, ImageDraw, ImageFilter, ImageFont
import sys

def process_image(input_image_path): # Function to process the image
    
    im = Image.open(input_image_path)
    
    gray_im = im.convert("L")  # Convert to grayscale
    
    # Create a new image for highlighting dark areas
    color_im = Image.new("RGB", (im.width, im.height), color=0)
    
    # Highlight very dark areas with red
    for x in range(im.width):
        for y in range(im.height):
            p = gray_im.getpixel((x, y))
            if p < 20:
                color_im.putpixel((x, y), (255, 0, 0))  # converting it into Red color
            else:
                color_im.putpixel((x, y), (p, p, p))  # Keeping it grayscale
    
    # Smoothing the image and detecting edges of the image 
    smoothed_im = color_im.filter(ImageFilter.SMOOTH)
    edges_im = smoothed_im.filter(ImageFilter.FIND_EDGES)
    edge_gray_im = edges_im.convert("L") # converting the edge images to gray scale 
    
    binary_im = edge_gray_im.point(lambda x: 255 if x > 80 else 0)
    
    # Apply erosion to remove noise
    eroded_im = binary_im.filter(ImageFilter.MaxFilter(1))
    
    return eroded_im, color_im

def detect_staff_lines(image, min_line_distance=5): # Function to detect staff lines in a music sheet
    width, height = image.size
    pixels = image.load()

    horizontal_projection = [0] * height
    for y in range(1, height-1):
        for x in range(1, width-1):
            if pixels[x, y] > 97:
                horizontal_projection[y] += 1

    threshold = max(horizontal_projection) * 0.5 # finding the line having more pixels on it 
    potential_lines = [y for y, value in enumerate(horizontal_projection) if value > threshold]

    # Filter out duplicate lines
    filtered_lines = []
    for line in potential_lines:
        if not filtered_lines or line - filtered_lines[-1] >= min_line_distance:
            filtered_lines.append(line)

    return filtered_lines

def draw_lines_on_image(image, lines):
    img = image.convert('RGB') # Converting to RGB so we can draw the color lines
    draw = ImageDraw.Draw(img)
    width, height = img.size

    for y in lines:
        draw.line((0, y, width, y), fill=(255, 0, 0), width=1)  # Red lines, thickness 1

    return img

def remove_duplicate_lines(lines):
    if len(lines) > 10:
        r_duplicate = [num for i, num in enumerate(lines) if i % 2 == 0] # removing the duplicate lines to keep the one line as edge detection of the image gave two lines
    else:
        r_duplicate = lines
    
    return r_duplicate

def find_all_notes(music_sheet_path, note_path, threshold=0.6): # Function to find occurrences of a given note in the music sheet with threshold 0.61 or 0.6 would be same 

    music_sheet = Image.open(music_sheet_path).convert("L")
    note = Image.open(note_path).convert("L")  # Convert to grayscale
    
    
    note_width, note_height = note.size
    music_sheet_width, music_sheet_height = music_sheet.size
    
    locations = [] # storing location
    correlations = []  # Store correlation values
    
    for x in range(music_sheet_width - note_width + 1):  # Perform template matching between the images 
        for y in range(music_sheet_height - note_height + 1):
            roi = music_sheet.crop((x, y, x + note_width, y + note_height)) # Extract a region of interest from the music sheet
            correlation = calculate_correlation(note, roi)
            
            if correlation >= threshold: # checking with the threshold value if it is valid 
                locations.append((x, y))
                correlations.append(correlation)
    
    return locations, correlations

def calculate_correlation(image1, image2): # Function to calculate the correlation between two images 
    
    width, height = image1.size
    sum_xy = sum_x = sum_y = sum_x2 = sum_y2 = 0
    
    for x in range(width):
        for y in range(height):
            pixel_x = image1.getpixel((x, y))
            pixel_y = image2.getpixel((x, y))
            
            sum_xy += pixel_x * pixel_y
            sum_x += pixel_x 
            sum_y += pixel_y
            sum_x2 += pixel_x ** 2
            sum_y2 += pixel_y ** 2
    
    numerator = (width * height * sum_xy) - (sum_x * sum_y)
    denominator = ((width * height * sum_x2 - sum_x ** 2) * (width * height * sum_y2 - sum_y ** 2)) ** 0.5
    
    return 0 if denominator == 0 else numerator / denominator # returns the calucalted the value of correlation 

# Function to filter overlapping detected objects using non-maximum suppression
def non_maximum_suppression(locations, correlations, note_width, note_height, overlap_threshold=0.5):
    detections = sorted(zip(locations, correlations), key=lambda x: x[1], reverse=True)
    filtered_locations = []
    
    while detections:
        best_location, best_correlation = detections.pop(0)
        filtered_locations.append(best_location)
        detections = [
            (loc, corr)
            for loc, corr in detections
            if not is_overlapping(best_location, (note_width, note_height), loc, (note_width, note_height), overlap_threshold)
        ]
    
    return filtered_locations

# Function to check if two detected objects are overlapping
def is_overlapping(box1_topleft, box1_size, box2_topleft, box2_size, overlap_threshold):
    x1, y1 = box1_topleft
    w1, h1 = box1_size
    x2, y2 = box2_topleft
    w2, h2 = box2_size
    
    x_left = max(x1, x2)
    y_top = max(y1, y2)
    x_right = min(x1 + w1, x2 + w2)
    y_bottom = min(y1 + h1, y2 + h2)
    
    if x_right < x_left or y_bottom < y_top:
        return False
    
    intersection_area = (x_right - x_left) * (y_bottom - y_top)
    box1_area = w1 * h1
    box2_area = w2 * h2
    overlap = intersection_area / min(box1_area, box2_area)
    
    return overlap > overlap_threshold

def draw_combined_shapes(music_sheet_path, red_locations, green_locations, blue_location, note_size, shape_size, shape1_size, staff_line):
    # Open the image and create a drawing object
    # Step 1: Split `a` into chunks of 5 elements
    a = staff_line
    b = red_locations
    chunks = [a[i:i+5] for i in range(0, len(a), 5)]
    max_values = [max(chunk) + 15 for chunk in chunks]  # e.g., [84 + 10, 205 + 10] -> [94, 215]

    # Step 2: Total number of lists
    total_lists = len(max_values)

    # Step 3: Create result lists based on ranges
    results = []
    results.append([pair for pair in b if pair[1] < max_values[0]])  # First list: < 94
    for i in range(1, len(max_values)):
        results.append([pair for pair in b if max_values[i-1] < pair[1] < max_values[i]])  # e.g., 94 < value < 215

    # Step 4: Setup for drawing (example image setup, adjust as needed)
    music_sheet = Image.open(music_sheet_path).convert("RGB")
    draw = ImageDraw.Draw(music_sheet)
    font = ImageFont.truetype("./part2/Arial_Bold.ttf", 12)  # Use a proper font if available
    note_width, note_height = note_size
    shape_width, shape_height = shape_size
    shape1_width, shape1_height = shape1_size

    # Step 5: Process each coordinate and assign `k` based on the value
    with open('./part2/detected.txt', 'w') as file:  # Open file once before the loop
        for idx, (x, y) in enumerate(red_locations):
            if idx >= len(b):  # Ensure we don't exceed the number of pairs in `b`
                break
            pair = b[idx]  # Get the corresponding pair from `b`
            value = pair[1]  # Extract the value to compare
            k = ""  # Default value

            # Find which chunk this value belongs to by checking `results`
            for i, result in enumerate(results):
                if pair in result:  # If this pair is in the current result list
                    chunk = chunks[i]
                    a_idx = 0  # Reset chunk index
                    if i % 2 == 0:
                        # Assign `k` based on the comparison logic
                        if value < (chunk[a_idx] - 5):
                            k = "B"
                        elif (chunk[a_idx] - 5) <= value < chunk[a_idx + 1]:
                            k = "D"
                        elif chunk[a_idx + 1] <= value < chunk[a_idx + 2]:
                            k = "B"
                        elif (chunk[a_idx + 2]-2) <= value < (chunk[a_idx + 3]-8):
                            k = "A"
                        elif chunk[a_idx + 2] <= value < chunk[a_idx + 3]:
                            k = "G"
                        elif chunk[a_idx + 3] <= value < chunk[a_idx + 4]:
                            k = "G"
                        elif chunk[a_idx + 4] >= value >= (chunk[a_idx + 4] - 5):
                            k = "D"
                        elif value < (chunk[a_idx + 4] + 5):
                            k = "B"
                        else:
                            k = "B"
                    else:
                        if value < (chunk[a_idx] - 15):
                            k = "C"
                        elif (chunk[a_idx] - 15) <= value < chunk[a_idx]:
                            k = "B"
                        elif chunk[a_idx] <= value < chunk[a_idx+1]:
                            k = "G"
                        elif chunk[a_idx+1] <= value < chunk[a_idx+2]:
                            k = "D"
                        elif chunk[a_idx+2] <= value < chunk[a_idx+3]:
                            k = "A"
                        elif chunk[a_idx+3] <= value < chunk[a_idx+4]:
                            k = "G"
                        else:
                            k = " "

                    # Draw the rectangle and text with the computed `k`
                    draw.rectangle((x, y, x + note_width, y + note_height), outline="red", width=3)
                    draw.text((x - 13, y + note_height // 3), k, fill="red", font=font)
            
                    # Write to file (file is already open, so this appends a new line)
                    file.write(f"{x} {y} {note_height} {note_width} {k} 0.0\n")
        
    # Draw green rectangles
    with open('./part2/detected.txt', 'a') as file:
        for xx, yy in green_locations:
            draw.rectangle((xx, yy, xx + shape_width, yy + shape_height), outline=(144, 238, 144), width=3)
            file.write(f"{xx} {yy} {shape_height} {shape_width} Green 0.0\n")
        
    # Draw blue rectangles
    with open('./part2/detected.txt', 'a') as file:
        for xxx, yyy in blue_location:
            draw.rectangle((xxx, yyy, xxx + shape1_width, yyy + shape1_height), outline="blue", width=3)
            file.write(f"{xxx} {yyy} {shape1_height} {shape1_width} Blue 0.0\n")
    
    return music_sheet

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception("Error: Please provide input image paths as parameters.\n"
                        "Example: python3 script_name.py input.jpg")
    
    input_image_path = sys.argv[1]
    note_path = "./part2/note.png"
    shape_path = "./part2/shape.png"
    shape1_path = "./part2/shape1.png"
    
    # Process the image
    processed_image, color_image = process_image(input_image_path)
    
    # Detect staff lines
    staff_lines = detect_staff_lines(processed_image)
    
    # Remove duplicate lines
    filtered_lines = remove_duplicate_lines(staff_lines)
    
    # Draw lines on the image
    image_with_lines = draw_lines_on_image(processed_image, filtered_lines)
    
    # Find notes
    locations, correlations = find_all_notes(input_image_path, note_path)
    note = Image.open(note_path)
    note_width, note_height = note.size
    filtered_locations = non_maximum_suppression(locations, correlations, note_width, note_height, overlap_threshold=0.5)
    
    # Find shape
    ll, cr = find_all_notes(input_image_path, shape_path)
    shape = Image.open(shape_path)
    shape_width, shape_height = shape.size
    f_l = non_maximum_suppression(ll, cr, shape_width, shape_height, overlap_threshold=0.5)
    
    # Find shape1
    ll1, cr1 = find_all_notes(input_image_path, shape1_path)
    shape1 = Image.open(shape1_path)
    shape1_width, shape1_height = shape1.size
    f_l1 = non_maximum_suppression(ll1, cr1, shape1_width, shape1_height, overlap_threshold=0.5)
    
    # Draw rectangles around notes and shape
    final_image = draw_combined_shapes(input_image_path, filtered_locations, f_l, f_l1, (note_width, note_height), (shape_width, shape_height), (shape1_width, shape1_height), filtered_lines)
    
    # Save the output images
    image_with_lines.save("./part2/staff_lines_detected.png")
    final_image.save("./part2/notes_detected.png")

