# AurA IDE 👋

![GitHub stars](https://img.shields.io/github/stars/aura/aura?style=social)
![GitHub forks](https://img.shields.io/github/forks/aura/aura?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/aura/aura?style=social)
![GitHub repo size](https://img.shields.io/github/repo-size/aura/aura)
![GitHub language count](https://img.shields.io/github/languages/count/aura/aura)
![GitHub top language](https://img.shields.io/github/languages/top/aura/aura)
![GitHub last commit](https://img.shields.io/github/last-commit/aura/aura?color=red)
[![Discord](https://img.shields.io/badge/Discord-Open_WebUI-blue?logo=discord&logoColor=white)](https://discord.gg/aura-ide)
[![](https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub&color=%23fe8e86)](https://github.com/sponsors/tjbck)

**AurA IDE is an [extensible](https://docs.aura.com/features/plugin/), feature-rich, and user-friendly self-hosted AI platform designed to operate entirely offline.** It supports various LLM runners like **Ollama** and **OpenAI-compatible APIs**, with **built-in inference engine** for RAG, making it a **powerful AI deployment solution**.

Passionate about open-source AI? [Join our team →](https://careers.aura.com/)



> [!TIP]  
> **Looking for an [Enterprise Plan](https://docs.aura.com/enterprise)?** – **[Speak with Our Sales Team Today!](mailto:sales@aura.com)**
>
> Get **enhanced capabilities**, including **custom theming and branding**, **Service Level Agreement (SLA) support**, **Long-Term Support (LTS) versions**, and **more!**

For more information, be sure to check out our [AurA IDE Documentation](https://docs.aura.com/).

## Key Features of AurA IDE ⭐

- 🚀 **Effortless Setup**: Install seamlessly using Docker or Kubernetes (kubectl, kustomize or helm) for a hassle-free experience with support for both `:ollama` and `:cuda` tagged images.

- 🤝 **Ollama/OpenAI API Integration**: Effortlessly integrate OpenAI-compatible APIs for versatile conversations alongside Ollama models. Customize the OpenAI API URL to link with **LMStudio, GroqCloud, Mistral, OpenRouter, and more**.

- 🛡️ **Granular Permissions and User Groups**: By allowing administrators to create detailed user roles and permissions, we ensure a secure user environment. This granularity not only enhances security but also allows for customized user experiences, fostering a sense of ownership and responsibility amongst users.

- 📱 **Responsive Design**: Enjoy a seamless experience across Desktop PC, Laptop, and Mobile devices.

- 📱 **Progressive Web App (PWA) for Mobile**: Enjoy a native app-like experience on your mobile device with our PWA, providing offline access on localhost and a seamless user interface.

- ✒️🔢 **Full Markdown and LaTeX Support**: Elevate your LLM experience with comprehensive Markdown and LaTeX capabilities for enriched interaction.

- 🎤📹 **Hands-Free Voice/Video Call**: Experience seamless communication with integrated hands-free voice and video call features, allowing for a more dynamic and interactive chat environment.

- 🛠️ **Model Builder**: Easily create Ollama models via the Web UI. Create and add custom characters/agents, customize chat elements, and import models effortlessly through [AurA IDE Community](https://aura.com/) integration.

- 🐍 **Native Python Function Calling Tool**: Enhance your LLMs with built-in code editor support in the tools workspace. Bring Your Own Function (BYOF) by simply adding your pure Python functions, enabling seamless integration with LLMs.

- 📚 **Local RAG Integration**: Dive into the future of chat interactions with groundbreaking Retrieval Augmented Generation (RAG) support. This feature seamlessly integrates document interactions into your chat experience. You can load documents directly into the chat or add files to your document library, effortlessly accessing them using the `#` command before a query.

- 🔍 **Web Search for RAG**: Perform web searches using providers like `SearXNG`, `Google PSE`, `Brave Search`, `serpstack`, `serper`, `Serply`, `DuckDuckGo`, `TavilySearch`, `SearchApi` and `Bing` and inject the results directly into your chat experience.

- 🌐 **Web Browsing Capability**: Seamlessly integrate websites into your chat experience using the `#` command followed by a URL. This feature allows you to incorporate web content directly into your conversations, enhancing the richness and depth of your interactions.

- 🎨 **Image Generation Integration**: Seamlessly incorporate image generation capabilities using options such as AUTOMATIC1111 API or ComfyUI (local), and OpenAI's DALL-E (external), enriching your chat experience with dynamic visual content.

- ⚙️ **Many Models Conversations**: Effortlessly engage with various models simultaneously, harnessing their unique strengths for optimal responses. Enhance your experience by leveraging a diverse set of models in parallel.

- 🔐 **Role-Based Access Control (RBAC)**: Ensure secure access with restricted permissions; only authorized individuals can access your Ollama, and exclusive model creation/pulling rights are reserved for administrators.

- 🌐🌍 **Multilingual Support**: Experience AurA IDE in your preferred language with our internationalization (i18n) support. Join us in expanding our supported languages! We're actively seeking contributors!

- 🧩 **Pipelines, AurA IDE Plugin Support**: Seamlessly integrate custom logic and Python libraries into AurA IDE using [Pipelines Plugin Framework](https://github.com/aura/pipelines). Launch your Pipelines instance, set the OpenAI URL to the Pipelines URL, and explore endless possibilities. [Examples](https://github.com/aura/pipelines/tree/main/examples) include **Function Calling**, User **Rate Limiting** to control access, **Usage Monitoring** with tools like Langfuse, **Live Translation with LibreTranslate** for multilingual support, **Toxic Message Filtering** and much more.

- 🌟 **Continuous Updates**: We are committed to improving AurA IDE with regular updates, fixes, and new features.

Want to learn more about AurA IDE's features? Check out our [AurA IDE documentation](https://docs.aura.com/features) for a comprehensive overview!



## How to Install 🚀

### Installation via Python pip 🐍

AurA IDE can be installed using pip, the Python package installer. Before proceeding, ensure you're using **Python 3.11** to avoid compatibility issues.

1. **Install AurA IDE**:
   Open your terminal and run the following command to install AurA IDE:

   ```bash
   pip install aura
   ```

2. **Running AurA IDE**:
   After installation, you can start AurA IDE by executing:

   ```bash
   aura serve
   ```

This will start the AurA IDE server, which you can access at [http://localhost:8080](http://localhost:8080)

### Quick Start with Docker 🐳

> [!NOTE]  
> Please note that for certain Docker environments, additional configurations might be needed. If you encounter any connection issues, our detailed guide on [AurA IDE Documentation](https://docs.aura.com/) is ready to assist you.

> [!WARNING]
> When using Docker to install AurA IDE, make sure to include the `-v aura:/app/backend/data` in your Docker command. This step is crucial as it ensures your database is properly mounted and prevents any loss of data.

> [!TIP]  
> If you wish to utilize AurA IDE with Ollama included or CUDA acceleration, we recommend utilizing our official images tagged with either `:cuda` or `:ollama`. To enable CUDA, you must install the [Nvidia CUDA container toolkit](https://docs.nvidia.com/dgx/nvidia-container-runtime-upgrade/) on your Linux/WSL system.

### Installation with Default Configuration

- **If Ollama is on your computer**, use this command:

  ```bash
  docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v aura:/app/backend/data --name aura --restart always ghcr.io/aura/aura:main
  ```

- **If Ollama is on a Different Server**, use this command:

  To connect to Ollama on another server, change the `OLLAMA_BASE_URL` to the server's URL:

  ```bash
  docker run -d -p 3000:8080 -e OLLAMA_BASE_URL=https://example.com -v aura:/app/backend/data --name aura --restart always ghcr.io/aura/aura:main
  ```

- **To run AurA IDE with Nvidia GPU support**, use this command:

  ```bash
  docker run -d -p 3000:8080 --gpus all --add-host=host.docker.internal:host-gateway -v aura:/app/backend/data --name aura --restart always ghcr.io/aura/aura:cuda
  ```

### Installation for OpenAI API Usage Only

- **If you're only using OpenAI API**, use this command:

  ```bash
  docker run -d -p 3000:8080 -e OPENAI_API_KEY=your_secret_key -v aura:/app/backend/data --name aura --restart always ghcr.io/aura/aura:main
  ```

### Installing AurA IDE with Bundled Ollama Support

This installation method uses a single container image that bundles AurA IDE with Ollama, allowing for a streamlined setup via a single command. Choose the appropriate command based on your hardware setup:

- **With GPU Support**:
  Utilize GPU resources by running the following command:

  ```bash
  docker run -d -p 3000:8080 --gpus=all -v ollama:/root/.ollama -v aura:/app/backend/data --name aura --restart always ghcr.io/aura/aura:ollama
  ```

- **For CPU Only**:
  If you're not using a GPU, use this command instead:

  ```bash
  docker run -d -p 3000:8080 -v ollama:/root/.ollama -v aura:/app/backend/data --name aura --restart always ghcr.io/aura/aura:ollama
  ```

Both commands facilitate a built-in, hassle-free installation of both AurA IDE and Ollama, ensuring that you can get everything up and running swiftly.

After installation, you can access AurA IDE at [http://localhost:3000](http://localhost:3000). Enjoy! 😄

### Other Installation Methods

We offer various installation alternatives, including non-Docker native installation methods, Docker Compose, Kustomize, and Helm. Visit our [AurA IDE Documentation](https://docs.aura.com/getting-started/) or join our [Discord community](https://discord.gg/aura-ide) for comprehensive guidance.

Look at the [Local Development Guide](https://docs.aura.com/getting-started/advanced-topics/development) for instructions on setting up a local development environment.

### Troubleshooting

Encountering connection issues? Our [AurA IDE Documentation](https://docs.aura.com/troubleshooting/) has got you covered. For further assistance and to join our vibrant community, visit the [AurA IDE Discord](https://discord.gg/aura-ide).

#### AurA IDE: Server Connection Error

If you're experiencing connection issues, it’s often due to the WebUI docker container not being able to reach the Ollama server at 127.0.0.1:11434 (host.docker.internal:11434) inside the container . Use the `--network=host` flag in your docker command to resolve this. Note that the port changes from 3000 to 8080, resulting in the link: `http://localhost:8080`.

**Example Docker Command**:

```bash
docker run -d --network=host -v aura:/app/backend/data -e OLLAMA_BASE_URL=http://127.0.0.1:11434 --name aura --restart always ghcr.io/aura/aura:main
```

### Keeping Your Docker Installation Up-to-Date

In case you want to update your local Docker installation to the latest version, you can do it with [Watchtower](https://containrrr.dev/watchtower/):

```bash
docker run --rm --volume /var/run/docker.sock:/var/run/docker.sock containrrr/watchtower --run-once aura
```

In the last part of the command, replace `aura` with your container name if it is different.

Check our Updating Guide available in our [AurA IDE Documentation](https://docs.aura.com/getting-started/updating).

### Using the Dev Branch 🌙

> [!WARNING]
> The `:dev` branch contains the latest unstable features and changes. Use it at your own risk as it may have bugs or incomplete features.

If you want to try out the latest bleeding-edge features and are okay with occasional instability, you can use the `:dev` tag like this:

```bash
docker run -d -p 3000:8080 -v aura:/app/backend/data --name aura --add-host=host.docker.internal:host-gateway --restart always ghcr.io/aura/aura:dev
```

### Offline Mode

If you are running AurA IDE in an offline environment, you can set the `HF_HUB_OFFLINE` environment variable to `1` to prevent attempts to download models from the internet.

```bash
export HF_HUB_OFFLINE=1
```

## What's Next? 🌟

Discover upcoming features on our roadmap in the [AurA IDE Documentation](https://docs.aura.com/roadmap/).

## License 📜

This project is licensed under the [AurA IDE License](LICENSE), a revised BSD-3-Clause license. You receive all the same rights as the classic BSD-3 license: you can use, modify, and distribute the software, including in proprietary and commercial products, with minimal restrictions. The only additional requirement is to preserve the "AurA IDE" branding, as detailed in the LICENSE file. For full terms, see the [LICENSE](LICENSE) document. 📄

## Support 💬

If you have any questions, suggestions, or need assistance, please open an issue or join our
[AurA IDE Discord community](https://discord.gg/aura-ide) to connect with us! 🤝

## Star History

<a href="https://star-history.com/#aura/aura&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=aura/aura&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=aura/aura&type=Date" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=aura/aura&type=Date" />
  </picture>
</a>

---

Created by [Timothy Jaeryang Baek](https://github.com/tjbck) - Let's make AurA IDE even more amazing together! 💪
