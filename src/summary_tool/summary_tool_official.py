

def display_tool(sample_urls, sample_prices):
    import requests
    from PIL import Image
    import matplotlib
    import matplotlib.pyplot as plt
    import numpy as np
    from io import BytesIO
    import os
    from fetch_and_extract_image import extrate_images

    # Set matplotlib backend to avoid display issues
    try:
        # Try to use a backend that works well on different systems
        if os.name == 'nt':  # Windows
            matplotlib.use('TkAgg')
        else:
            matplotlib.use('Agg')  # For headless systems
    except:
        pass

    def display_images_with_prices(image_urls, prices, columns=3, figsize=(15, 10), save_path=None):
        """
        Downloads images from URLs and displays them in a grid with their corresponding prices.

        Parameters:
        image_urls (list): List of image URLs to download
        prices (list): List of prices/values corresponding to each image
        columns (int): Number of columns in the display grid (default: 3)
        figsize (tuple): Figure size for the display (default: (15, 10))
        save_path (str): Optional path to save the figure instead of displaying

        Returns:
        list: Downloaded images as PIL Image objects
        """

        if len(image_urls) != len(prices):
            raise ValueError("Number of images and prices must be equal")

        if len(image_urls) == 0:
            print("No images to display")
            return []

        # Calculate number of rows needed
        rows = (len(image_urls) + columns - 1) // columns

        # Create figure
        fig = plt.figure(figsize=figsize)

        # Download and display images
        downloaded_images = []

        for i, (url, price) in enumerate(zip(image_urls, prices)):
            try:
                # Download image
                print(f"Downloading image {i + 1}/{len(image_urls)}...")
                response = requests.get(url, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                response.raise_for_status()

                # Open image from bytes
                image = Image.open(BytesIO(response.content))

                # Convert to RGB if necessary
                if image.mode != 'RGB':
                    image = image.convert('RGB')

                downloaded_images.append(image)

                # Create subplot
                ax = fig.add_subplot(rows, columns, i + 1)

                # Display image
                ax.imshow(np.array(image))
                ax.set_title(f"Price: ${price}", fontsize=12, fontweight='bold', pad=10)
                ax.axis('off')

            except requests.exceptions.RequestException as e:
                print(f"Error downloading image {i + 1}: {e}")
                downloaded_images.append(None)

                # Create subplot for error
                ax = fig.add_subplot(rows, columns, i + 1)
                ax.text(0.5, 0.5, f"Failed to load\nPrice: ${price}",
                        ha='center', va='center', transform=ax.transAxes,
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"),
                        fontsize=10)
                ax.set_title(f"Price: ${price}", fontsize=12, fontweight='bold', pad=10)
                ax.axis('off')

            except Exception as e:
                print(f"Error processing image {i + 1}: {e}")
                downloaded_images.append(None)

                # Create subplot for error
                ax = fig.add_subplot(rows, columns, i + 1)
                ax.text(0.5, 0.5, f"Error processing\nPrice: ${price}",
                        ha='center', va='center', transform=ax.transAxes,
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral"),
                        fontsize=10)
                ax.set_title(f"Price: ${price}", fontsize=12, fontweight='bold', pad=10)
                ax.axis('off')

        plt.tight_layout()

        # Save or show the figure
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Figure saved to {save_path}")
        else:
            plt.show(block=False)  # Non-blocking show

            # Wait for user input to close
            try:
                user_input = input("\nPress Enter to close the images or type 'save' to save them: ").strip().lower()

                if user_input == 'save':
                    filename = input("Enter filename (without extension): ").strip()
                    if not filename:
                        filename = "images_with_prices"
                    save_path = f"{filename}.png"
                    plt.savefig(save_path, dpi=300, bbox_inches='tight')
                    print(f"Images saved to {save_path}")
            except KeyboardInterrupt:
                print("\nClosing images...")
            finally:
                plt.close(fig)  # Close the specific figure

        return downloaded_images

    def display_images_with_prices_interactive(image_urls, prices, columns=3, figsize=(15, 10)):
        """
        Interactive version with matplotlib's built-in close functionality.
        """

        if len(image_urls) != len(prices):
            raise ValueError("Number of images and prices must be equal")

        if len(image_urls) == 0:
            print("No images to display")
            return []

        # Calculate number of rows needed
        rows = (len(image_urls) + columns - 1) // columns

        # Create figure with close button
        fig, axes = plt.subplots(rows, columns, figsize=figsize)
        fig.suptitle("Product Images and Prices - Close window when done", fontsize=16, fontweight='bold')

        # Handle single subplot case
        if rows == 1 and columns == 1:
            axes = [axes]
        elif rows == 1 or columns == 1:
            axes = axes.flatten()
        else:
            axes = axes.flatten()

        # Download and display images
        downloaded_images = []

        for i, (url, price) in enumerate(zip(image_urls, prices)):
            try:
                # Download image
                print(f"Downloading image {i + 1}/{len(image_urls)}...")
                response = requests.get(url, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                response.raise_for_status()

                # Open image from bytes
                image = Image.open(BytesIO(response.content))

                # Convert to RGB if necessary
                if image.mode != 'RGB':
                    image = image.convert('RGB')

                downloaded_images.append(image)

                # Display image
                axes[i].imshow(np.array(image))
                axes[i].set_title(f"Price: ${price}", fontsize=12, fontweight='bold', pad=10)
                axes[i].axis('off')

            except Exception as e:
                print(f"Error processing image {i + 1}: {e}")
                downloaded_images.append(None)

                # Display error message
                axes[i].text(0.5, 0.5, f"Error loading\nPrice: ${price}",
                             ha='center', va='center', transform=axes[i].transAxes,
                             bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"),
                             fontsize=10)
                axes[i].set_title(f"Price: ${price}", fontsize=12, fontweight='bold', pad=10)
                axes[i].axis('off')

        # Hide unused subplots
        for i in range(len(image_urls), len(axes)):
            axes[i].set_visible(False)

        plt.tight_layout()

        # Show with blocking (waits for user to close window)
        print("\n" + "=" * 50)
        print("Images displayed! You can:")
        print("1. Close the window to continue")
        print("2. Press Ctrl+C in terminal to force close")
        print("=" * 50)

        try:
            plt.show()  # Blocking show - waits for window to be closed
        except KeyboardInterrupt:
            print("\nForced close by user")
            plt.close('all')

        return downloaded_images
    def display_images_console_interactive(image_urls, prices):
        """
        Console version that shows image info and waits for user input.
        """
        if len(image_urls) != len(prices):
            raise ValueError("Number of images and prices must be equal")

        downloaded_images = []

        print("\n" + "=" * 60)
        print("DOWNLOADING AND DISPLAYING PRODUCT INFORMATION")
        print("=" * 60)

        for i, (url, price) in enumerate(zip(image_urls, prices)):
            try:
                print(f"\nProduct {i + 1}:")
                print(f"  Price: ${price}")
                print(f"  Downloading from: {url[:50]}...")

                response = requests.get(url, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                response.raise_for_status()

                image = Image.open(BytesIO(response.content))
                if image.mode != 'RGB':
                    image = image.convert('RGB')

                downloaded_images.append({'image': image, 'price': price, 'url': url})
                print(f"  ✓ Successfully downloaded (Size: {image.size})")

            except Exception as e:
                print(f"  ✗ Error: {e}")
                downloaded_images.append({'image': None, 'price': price, 'url': url})

        print("\n" + "=" * 60)
        print("SUMMARY:")
        successful = len([img for img in downloaded_images if img['image'] is not None])
        print(f"Successfully downloaded: {successful}/{len(image_urls)} images")

        for i, item in enumerate(downloaded_images):
            status = "✓" if item['image'] else "✗"
            print(f"  {status} Product {i + 1}: ${item['price']}")

        print("=" * 60)

        # Wait for user input
        try:
            input("\nPress Enter to continue...")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")

        return downloaded_images

    url_images = [extrate_images(sample_url) for sample_url in sample_urls]
    print(url_images)
    images = display_images_with_prices_interactive(url_images, sample_prices, columns=len(sample_urls))
    choice = input("Your choice : ")
    return sample_urls[int(choice)]


# Example usage
if __name__ == "__main__":
    # Sample data
    sample_urls = [
        "https://www.nike.com/fr/t/chaussure-p-6000-T6ofxOFZ/FD9876-101?cp=10777067101_search_&Macro=--o-361508208-1176478328680660-e-c-FR-csscore--pla-4577129470675250-189521-00196604969376&ds_rl=1252249&msclkid=89f44dd2070e15832025259cb4001ec6&gclid=89f44dd2070e15832025259cb4001ec6&gclsrc=3p.ds&gad_source=7",
        "https://www.nike.com/fr/t/chaussure-p-6000-T6ofxOFZ/FD9876-101?cp=10777067101_search_&Macro=--o-361508208-1176478328680660-e-c-FR-csscore--pla-4577129470675250-189521-00196604969376&ds_rl=1252249&msclkid=89f44dd2070e15832025259cb4001ec6&gclid=89f44dd2070e15832025259cb4001ec6&gclsrc=3p.ds&gad_source=7"
    ]
    sample_prices = [29.99, 45.50]

    print(display_tool(sample_urls, sample_prices))