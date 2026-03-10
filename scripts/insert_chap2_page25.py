import os

html_path = r"c:\Users\keysh\github\telugu4nontelugu\class6\02_Manamantaa_Okkate\exercise.html"

with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

words = [
    ("అల", "Ala", "Wave"), ("ఆలయం", "Aalayam", "Temple"), ("ఉంగరం", "Ungaram", "Ring"), ("ఈల", "Eela", "Whistle"),
    ("ఊయల", "Ooyala", "Cradle"), ("శంఖం", "Shankham", "Conch"), ("లవంగం", "Lavangam", "Clove"), ("రథం", "Ratham", "Chariot"),
    ("కంఠం", "Kantham", "Throat"), ("భవనం", "Bhavanam", "Building"), ("ఫలం", "Phalam", "Fruit"), ("కంకణం", "Kankanam", "Bangle"),
    ("ధనం", "Dhanam", "Wealth"), ("కలశం", "Kalasham", "Sacred Pot"), ("పనస", "Panasa", "Jackfruit"), ("దళం", "Dalam", "Petal/Leafage"),
    ("ఢంకా", "Dhanka", "Large Drum"), ("వడ", "Vada", "Vada"), ("కమలం", "Kamalam", "Lotus"), ("పంజరం", "Panjaram", "Cage")
]

grid_html = ""
for tel, eng, meaning in words:
    grid_html += f"""                    <div class="grid-item">
                        <span class="telugu-text">{tel}</span>
                        <span class="english-text">{eng}</span>
                        <button class="speak-btn" style="margin: 5px auto;" onclick="speakTelugu('{tel}', this)">🔊</button>
                    </div>\n"""

new_q11_block = f"""        <!-- Question 11 (Picture reading from page 25) -->
        <div class="qa-block">
            <div class="qa-header">
                <span class="section-label">Q 11 (ఈ)</span>
                <span class="qa-text">
                    <span class="telugu-text">కింది బొమ్మల ఆధారంగా పదాలను చదవండి. వాటిలోని అక్షరాలను వర్ణమాల చార్టులో చూపండి.</span>
                    <span class="english-text">Read the words based on the following pictures. Show the letters in the alphabet chart.</span>
                </span>
                <button class="speak-btn" onclick="speakTelugu('కింది బొమ్మల ఆధారంగా పదాలను చదవండి. వాటిలోని అక్షరాలను వర్ణమాల చార్టులో చూపండి', this)">🔊</button>
            </div>
            <div class="activity-box">
                <div class="grid-container" style="grid-template-columns: repeat(4, 1fr);">
{grid_html}                </div>
            </div>
        </div>

"""

insert_marker = "        <!-- Question 11 (Word grid from page 26) -->"

parts = html_content.split(insert_marker)
if len(parts) == 2:
    new_html = parts[0] + new_q11_block + "        <!-- Question 12 (Word grid from page 26) -->" + parts[1]
    
    # Renumber subsequent Qs
    new_html = new_html.replace("Q 11 (ఉ)", "Q 12 (ఉ)")
    new_html = new_html.replace("Q 12 (ఊ)", "Q 13 (ఊ)")
    new_html = new_html.replace("Question 12 (Frequency analysis)", "Question 13 (Frequency analysis)")
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(new_html)
    print("✅ Successfully inserted Q11 and shifted others!")
else:
    print("❌ Could not find insertion point!")
