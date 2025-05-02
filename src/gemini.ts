const SUPA_SECRETR_GEMINI_API_KEY = 'AIzaSyCRBTgWASk9nnlk_h6WPgmWekHxGIpvRCM';

const PUBLIC_URL = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${SUPA_SECRETR_GEMINI_API_KEY}`;

declare interface TextPart {
  text: string;
}

declare interface GenerateContentRequest {
  contents: Array<{
    parts: TextPart[];
  }>;
}

declare interface GenerateContentResponse {
  candidates: Array<{
    content: {
      parts: TextPart[];
    };
  }>;
}

/** Call Public Gemini model with the given prompt and return the text response. */
export async function callPublicGemini(input: string) {
  const body: GenerateContentRequest = {
    contents: [{ parts: [{ text: input }] }],
  };
  const response = await fetch(PUBLIC_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw new Error('Failed to generate content: ' + response.statusText);
  }
  const result: GenerateContentResponse = await response.json();
  console.log('result: ', result);

  return result.candidates[0].content.parts.map((part) => part.text).join('');
}
