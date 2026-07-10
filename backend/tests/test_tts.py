import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.tts import generate_tts

@pytest.mark.asyncio
async def test_generate_tts():
    sample_text = """
     Market çalışanıyım ve geçen gün öyle bir an yaşadım ki hala aklımdan çıkmıyor. Yedi yaşlarında oğluyla bir kadın geldi, çocuğun elinde sönmüş, perişan halde bir balon hayvan vardı. Kadın bana helyum tankımız olup olmadığını, balonu doldurup dolduramayacağımızı sordu. Üzgünüm, yok dedim. Kadın hemen sinirlendi, Peki şimdi ne yapacağım. Bütün gün bunun için ağladı, diye çıkıştı. Ben daha cevap veremeden çocuk, Sorun değil anneciğim, biraz yorgun olsa da balonumu hala çok seviyorum, dedi. Kadın bir an çocuğuna baktı ve sonra marketin ortasında basmaya başladı ağlamaya. Hani böyle çirkin çirkin ağlamak derler ya, tam öyle. Çocuk da annesinin sırtını okşayıp, Ağlama anneciğim, yenisini alırız, diyordu. Ben de elimde bir torba patatesle hayatla ne yapacağımı bilemez halde öylece dikildim kaldım.
    """
    
    audio_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "audio")
    os.makedirs(audio_dir, exist_ok=True)
    output_path = os.path.join(audio_dir, "test_audio.mp3")
    
    result_path = await generate_tts(text=sample_text, output_path=output_path)
    
    assert result_path is not None
    assert os.path.exists(result_path)
    
    # Check if the file is not empty (size > 0 bytes)
    file_size = os.path.getsize(result_path)
    assert file_size > 0, "Generated TTS audio file is empty!"
    
    print("\n" + "="*50)
    print("✅ TEST SUCCESSFUL! TTS AUDIO GENERATED:")
    print("="*50)
    print(f"Path: {result_path}")
    print(f"Size: {file_size} bytes")
    print("="*50 + "\n")
