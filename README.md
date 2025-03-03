## Identify the pitch

### Notes - 2/6 - Ideas
Here we have to find all round shapes in the image. Each of the filled in notes have the same thickness/diameter/circumference, which is different from the signs for clefs, brace and rests. We need to draw a bounding box surrounding each note. Then finally identify the pitch based on the line on which they are placed. The problem with pitch is that it varies with clef. So an 'E' in treble clef is a 'G' in base clef.  

### Notes - 2/8 (ukalvolu)
Worked on part 2 -> Created script that processes an input image to detect and highlight dark regions, and draws bounding boxes around the note heads (and other curve shapes), identified based on a threshold. Image processing tasks performed - grayscale conversion, binary thresholding, noise removal, edge detection, and filtering of detected points. The processed image is saved, along with the coordinates of the boxes. Next steps are to provide 

### Notes - 2/14 (ukalvolu)
1. I have updated `staff_normalizer.py` to detect staff lines and extract their y-coordinates. This information will be useful later when assigning values to notes during detection.

2. Initially, I applied a horizontal projection to the image to identify pixels with values greater than `97`. I arrived at this threshold by experimenting with different values to find an optimal one. Next, I applied a line of code to get the max of pixels which were on the same line.

3. However, in Image 3, some staff lines were blurred and could not be detected properly. To address this, I applied a `MaxFilter` to enhance the density of these lines, making them more prominent. This approach successfully captured the staff lines, positioning them correctly for the next steps.

I'm on track now, but I need to identify the shapes and determine their positions to assign them values. Next, I'll focus on detecting the notes and other symbols, assigning them values to complete Part 2.

### Notes - 2/15 (ukalvolu)
I was able to highlight the notes in the image and remove the maximum noises to detect them, but the detection is currently using the trail method. I need to understand how to teach a child to understand the notes because I believe the system is a child with vision who is learning how to detect the notes. As of now, I've tried cropping the image into (16,16) forms and detecting them with the threshold. It worked better for `music1.png` than others, but I need to tweak my technique to recognize the notes.

### Notes - 2/16 (ukalvolu)
I was able to detect the symbols and notes using a sampling of notes and shapes, matching them to the image and obtaining the `correlation` = `https://en.wikipedia.org/wiki/Pearson_correlation_coefficient` vlaue and tried several thresholds and came up with `0.61`, which was good for detecting specific places in'music1.png' but not so good for detecting notes in other images but accurate for forms. Then, as I was creating the bounding boxes, there was too much overlap, so I used a technique called `Non-Maximum Suppression` = `https://www.geeksforgeeks.org/what-is-non-maximum-suppression/` to remove the overelapping bounding boxes and filter their locations to give only one box at each position. Now, in the future, I need to detect the notes location and assign it a value using the prior staff detection location as reference. The code is taking too much time to detect I will look into it later.

### Notes - 2/21 (ukalvolu)
I have started detecting the notes and developed a prototype logic for it, which needs some minor fine-tuning. Additionally, create a `detected.txt` file containing all the necessary details as required.

### Notes - 2/22 (ukalvolu)
For `music1.png`, I successfully achieved exact note detection for the `treble staff`, and now I'm working on the `bass staff`. My plan is to divide the staff line array into five equal parts, assigning even-indexed parts to the `treble staff` and odd-indexed parts to the `bass staff`. This will allow me to apply different conditions for each.

However, there's an issue with `music2.png` because it contains only the `treble staff`. To address this, I plan to use the same note detection method for symbols, determine their coordinates, and then use those coordinates to assign values to the notes accordingly.

### Notes - 2/23 (ukalvolu)
I successfully achieved exact accuracy in match note detection for `music1.png`. However, the other images contained noise, making detection challenging. Despite this, I gained valuable insights into techniques such as Non-Maximum Suppression, image feature extraction, image alteration for specific requirements, and image mapping.
---
