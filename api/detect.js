export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { image } = req.body;
  if (!image) return res.status(200).json({ insect_name: 'No Image', bio: 'No image provided.' });

  try {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'gpt-4o-mini',
        max_tokens: 1000,
        messages: [{
          role: 'user',
          content: [
            { type: 'text', text: `You are an expert entomologist. Identify the insect in this image. Accept ALL real-world photos including phone camera shots. Do NOT reject images for quality. If an insect is held by hands or gloves focus only on the insect. Return ONLY raw JSON no markdown no backticks with these exact fields: insect_name, biological_name, genus, species, classification (object with kingdom phylum class order family genus species), confidence (decimal 0-1 based on actual certainty not always 0.95), danger_level (low/medium/high/unknown), school_risk_level (low/medium/high/unknown), diet, lifespan, habitat, population, economic_importance, bio. If no insect set insect_name to No Insect Detected. If unclear set insect_name to Unknown Insect.` },
            { type: 'image_url', image_url: { url: image } }
          ]
        }]
      })
    });

    const data = await response.json();

    if (data.error) {
      return res.status(200).json({ insect_name: 'Connection Issue', bio: 'AI is busy. Please try again.' });
    }

    const raw = data.choices[0].message.content;
    const cleaned = raw.replace(/```json|```/g, '').trim();
    const result = JSON.parse(cleaned);
    return res.status(200).json(result);

  } catch (e) {
    return res.status(200).json({ insect_name: 'Error', bio: `Something went wrong: ${e.message}` });
  }
}
