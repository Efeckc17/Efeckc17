import os
import json
import requests
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import io

CLOUDFLARE_API_TOKEN = os.getenv('CLOUDFLARE_TOKEN')
HEADERS = {
    'Authorization': f'Bearer {CLOUDFLARE_API_TOKEN}',
    'Content-Type': 'application/json',
}

def get_analytics():
    end = datetime.now()
    start = end - timedelta(days=7)
    
    query = """
    {
      viewer {
        zones(first: 1) {
          edges {
            node {
              httpRequests1dGroups(
                limit: 7
                filter: {
                  date_geq: "%s"
                  date_leq: "%s"
                }
              ) {
                dimensions {
                  date
                }
                sum {
                  requests
                  pageViews
                }
              }
            }
          }
        }
      }
    }
    """ % (start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))

    response = requests.post(
        'https://api.cloudflare.com/client/v4/graphql',
        headers=HEADERS,
        json={'query': query}
    )
    
    return response.json()

def create_analytics_image(data):
    width = 800
    height = 400
    
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    try:
        analytics = data['data']['viewer']['zones']['edges'][0]['node']['httpRequests1dGroups']
        
        total_views = sum(day['sum']['pageViews'] for day in analytics)
        
        text = f"Weekly Visitors: {total_views:,}"
        
        font_size = 48
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
            
        text_width = draw.textlength(text, font=font)
        x = (width - text_width) / 2
        y = (height - font_size) / 2
        
        draw.text((x, y), text, fill='black', font=font)
        
        image.save('cloudflare.png')
        
    except Exception as e:
        print(f"Error creating image: {e}")
        draw.text((10, 10), "Error fetching analytics", fill='black')
        image.save('cloudflare.png')

def main():
    try:
        data = get_analytics()
        create_analytics_image(data)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 