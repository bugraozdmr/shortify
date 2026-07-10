import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.tts import generate_tts

@pytest.mark.asyncio
async def test_generate_tts():
    sample_text = """
     Market çalışanı olarak birkaç gün önce yaşadığım olayı anlatayım size Bir kadın yedi yaşlarında oğluyla geldi çocuğun elinde sönmüş perişan halde bir balon hayvan vardı Annesi bana helyum tankımız olup olmadığını sordu balonu doldurmak istiyormuş Ben de üzülerek olmadığını söyledim Kadın hemen sinirlendi Şimdi ne yapacağım ben Çocuk bütün gün bunun için ağladı diye çıkıştı Daha ben cevap veremeden çocuk annesine döndü Sorun değil anneciğim biraz yorgun olsa da balonumu hala seviyorum dedi Annesi bir an çocuğa baktı ve sonra bir anda hüngür hüngür ağlamaya başladı Resmen marketin ortasında çirkin çirkin ağlıyordu Çocuk annesinin sırtını sıvazlayıp Ağlama anne yenisini alırız dedi Ben de elimde bir poşet patatesle hayatımda ne yapacağımı bilemez halde öylece durdum kaldım
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
