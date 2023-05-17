# KUE-video-compressor
KUE Video Compressor é um programa de compressão de vídeo que permite aos usuários reduzir o tamanho de seus arquivos de vídeo sem perder muita qualidade. Ele usa o ffmpeg para codificar os vídeos com aceleração de hardware da NVIDIA, AMD ou Intel, dependendo da placa gráfica do usuário.

## Como usar

1. Inicie o programa e arraste e solte um arquivo de vídeo na janela do programa ou clique na janela para selecionar um arquivo de vídeo usando o diálogo de arquivo.

2. Insira o tamanho desejado (em MB) para o arquivo de vídeo comprimido na caixa de texto "Tamanho (MB)".

3. Insira o FPS desejado para o arquivo de vídeo comprimido na caixa de texto "FPS".

4. Insira a resolução desejada (em pixels) para o arquivo de vídeo comprimido na caixa de texto "Resolução (px)".

5. Selecione o codec desejado (h264 ou h265) no menu suspenso "Codec".

6. Se desejar que o áudio seja removido do arquivo de vídeo comprimido, marque a caixa "Mutar vídeo".

7. Clique no botão "Comprimir" para iniciar a compressão do vídeo.

8. O programa exibirá uma animação enquanto o vídeo estiver sendo comprimido e atualizará a porcentagem de progresso em tempo real.

9. Quando a compressão estiver concluída, um novo arquivo de vídeo será criado com o sufixo "_compressed" adicionado ao nome do arquivo original.

## Requisitos

- Windows
- Placa gráfica NVIDIA, AMD ou Intel compatível com codificação de hardware
- Driver da placa gráfica atualizado
- ffmpeg
