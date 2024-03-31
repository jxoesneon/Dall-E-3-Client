import os
from openai import OpenAI

# Load API key from environment variable (recommended)
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    # Handle missing API key (e.g., prompt for input or redirect)
    raise ValueError("Missing OpenAI API Key! Set the 'OPENAI_API_KEY' environment variable.")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)


def generate_image(prompt, size="1024x1024", quality="standard"):
  """
  Generates an image using DALL-E 3 based on the provided prompt.

  Args:
      prompt: The text description of the desired image.
      size: The desired image resolution (default: 1024x1024).
      quality: The image quality (default: standard, options: standard, hd).

  Returns:
      The URL of the generated image on the OpenAI servers.

  Raises:
      openai.error.Error: If an error occurs during the API call.
  """
  try:
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,  # Number of images to generate (set to 1 for now)
        size=size,
        quality=quality,
    )
    image_url = response.data[0].url
    return image_url
  except OpenAI.error.Error as e:
    raise ValueError(f"Error generating image: {str(e)}")


# Example usage (assuming you have your API key set)
# prompt = "A photorealistic portrait of a cat wearing a top hat and monocle."
# image_url = generate_image(prompt)
# print(f"Generated image URL: {image_url}")
