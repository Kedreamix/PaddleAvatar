
# 使用streamlit对TTS + Wav2Lip版本进行操作
# 这一部分是Paddle已经完成的版本，部署后更容易操作
import os
import streamlit as st
from azure.cognitiveservices.speech import AudioDataStream, SpeechConfig, SpeechSynthesizer, SpeechSynthesisOutputFormat
from azure.cognitiveservices.speech.audio import AudioOutputConfig
import azure.cognitiveservices.speech as speechsdk
from ppgan.apps.wav2lip_predictor import Wav2LipPredictor
from paddlespeech.cli.tts import TTSExecutor

st.title("“数字人交互，与虚拟的自己互动”——用PaddleAvatar打造数字分身，探索人机交互的未来")

if 'generate_face' not in st.session_state:
    st.session_state.generate_face = False
if 'generate_audio' not in st.session_state:
    st.session_state.generate_audio = False

# 合成中
if 'generate_on_video' not in st.session_state:
    st.session_state.generate_on_video = False
    
def generate_on_video():
    st.session_state.generate_on_video = True
    
if 'generate_on_wav' not in st.session_state:
    st.session_state.generate_on_wav = False
    
def generate_on_wav():
    st.session_state.generate_on_wav = True

def azure_tts(text, voice_name = 'XiaochenNeural' , output = 'output.wav', speech_rate = 1, speech_pitch = 1, speech_style = 'general'):
    # 填入微软语音的密钥
    speech_key, service_region = "speech_key", "service_region"
    
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    
    # 设置config，保存的文件
    audio_config = AudioOutputConfig(filename=output)
    synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        
    speech_rate = int((speech_rate - 1)*100)
    speech_pitch = int((speech_pitch - 1)*50)
    language = 'zh-CN'
    voice_name = language + '-'+ voice_name

    ssml = f'''<speak xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xmlns:emo="http://www.w3.org/2009/10/emotionml" version="1.0" xml:lang="en-US">
    <voice name="{voice_name}">'''
    speech_style = speech_style.lower()
    if speech_style != 'general':
        speech_style = speech_style.replace(' ', '')
        ssml += f'<mstts:express-as style="{speech_style}" >'
    ssml += f'''<prosody rate="{speech_rate}%" pitch="{speech_pitch}%">{text}
    </prosody></voice></speak>'''
    
    result = synthesizer.speak_ssml_async(ssml).get()
    stream = AudioDataStream(result)
    stream.save_to_wav_file(output)

# 使用paddlespeech的TTS
def paddlespeech_tts(text, voc, spk_id = 174, lang = 'zh', male=False):
    tts_executor = TTSExecutor()
    if male:
        wav_file = tts_executor(
        text = text,
        output = 'output.wav',
        am = 'fastspeech2_male',
        voc = 'pwgan_male',
        #use_onnx=use_onnx
        )
        return wav_file
    use_onnx = True
    am = 'tacotron2'
    voc = voc.lower()
    # 混合中文英文
    if lang == 'mix':
        am += 'fastspeech2_mix'
        voc += '_aishell3'
        use_onnx = False
    # 英文语音合成
    elif lang == 'en':
        am += '_ljspeech'
        voc += '_ljspeech'
    # 中文语音合成
    elif lang == 'zh':
        am += '_aishell3'
        voc += '_aishell3'
    # 语音合成
    wav_file = tts_executor(
        text = text,
        output = 'output.wav',
        am = am,
        voc = voc,
        lang = lang,
        spk_id = spk_id,
        use_onnx=use_onnx
        )
    return wav_file

                              
def wav2lip(input_face, input_audio, output = 'result.mp4'):
    #使用PaddleSpeech的Wav2Lip
    wav2lip_predictor = Wav2LipPredictor(face_det_batch_size = 4,
                                     wav2lip_batch_size = 8,
                                     face_enhancement = True)
    wav2lip_predictor.run(input_face, input_audio, output)
    return output

st.markdown("<hr />",unsafe_allow_html=True)
st.write("利用Wav2lip进行生成，请输入图片/视频 和 语音")
tab1, tab2 = st.tabs(["图片/视频", "语音/文字"])
with tab1:
    face = st.file_uploader("输入图片或者视频", type=['jpg', 'png', 'jpeg','mp4'])
    if face:
        save_face = face.name
        if 'mp4' in face.type:
            st.video(face)
        else:
            st.image(face)
        with open(save_face, 'wb') as f:
            f.write(face.read())
        st.session_state.generate_face = True
with tab2:
    choice = st.selectbox("请选择生成语音还是文字进行生成", ["微软Azure","PaddleSpeech语音合成","上传音频Audio"])
    if choice == '微软Azure':
        save_audio = 'output.wav'
        st.markdown("<hr />",unsafe_allow_html=True)
        st.markdown("""
        微软的语音技术包括多种产品，如微软的语音识别服务，可以将人的语音转化为文字；
        还有微软的语音合成服务，可以将文字转化为人的语音。这些技术可以应用于各种领域，如辅助视障人群使用计算机，在线教育，智能客服等。微软还提供语音技术的开发工具包，方便开发者使用这些技术创建各种应用。
        """)

        st.markdown("<hr />",unsafe_allow_html=True)
        text = st.text_input("输入文本", value = '''你可将此文本替换为所需的任何文本。你可在此文本框中编写或在此处粘贴你自己的文本。
        试用不同的语言和声音。改变语速和音调。
        请尽情使用文本转语音功能！''')

        # st.markdown("<hr />",unsafe_allow_html=True)
        voice = st.selectbox(
            '语音',
            ('XiaoxiaoNeural','XiaoyouNeural','XiaoqiuNeural','XiaoshuangNeural',
            'XiaoruiNeural','XiaohanNeural','XiaoxuanNeural','XiaoyanNeural',
            'XiaomoNeural','XiaochenNeural',
            'YunyeNeural','YunxiNeural','YunyangNeural'))

        stype = st.selectbox(label="说法风格",options=("General","Assistant","Chat","Customer Service",
                                                "Newscast","Affectionate","Angry","Calm","Cheerful","Disgruntled","Fearful",
                                                "Gentle","Lyrical","Sad","Serious","Poetry-reading"))

        rate = st.slider(label = '语速', min_value= 0.00,  max_value=3.00, value = 1.00, step = 0.01)
        pitch = st.slider(label = '音调', min_value= 0.00,  max_value= 2.00, value = 1.00, step=0.02)

        st.markdown("<hr />",unsafe_allow_html=True)        
        st.button("开始合成音频", on_click = generate_on_wav)
        label = st.empty()
        if st.session_state.generate_on_wav:
            label.warning('音频合成中，请耐心等待！')
            azure_tts(text, voice_name = voice , output = save_audio, speech_rate= rate, speech_pitch=pitch) # 生成自己的TTS语音
            
            st.session_state.generate_on_wav = False
            st.session_state.generate_audio = True
            label.success('音频合成成功！！！')
            
        if os.path.exists(save_audio):
            st.audio(save_audio)
            with open(save_audio,'rb') as file:
                st.download_button(
                    label="Download Audio",
                    data=file,
                    file_name=save_audio,
                    # mime='',
                )
    elif choice == 'PaddleSpeech语音合成':
        save_audio = "output.wav"
        
        tab3, tab4 = st.tabs(["高质量男声音色", "多种音色"])
        with tab4:
            st.markdown("""
    声码器说明：这里预制了三种声码器【PWGan】【WaveRnn】【HifiGan】, 三种声码器效果和生成时间有比较大的差距，请跟进自己的需要进行选择。

    | 声码器 | 音频质量 | 生成速度 |
    | :----: | :----: | :----: |
    | PWGan | 中等 | 中等 |
    | WaveRnn | 高 | 非常慢（耐心等待） |
    | HifiGan | 低 | 快 |

    """)
            st.markdown("<hr />",unsafe_allow_html=True)
            text = st.text_input("输入文本，支持中英双语！", value = "你好，我是数字人分身，很搞笑认识大家！")

            male = False
            voc = st.selectbox(
                '选择声码器',
                ('HifiGan','PWGan'))

            lang = st.selectbox(
                '选择语言）',
                ('zh','mix','en'))

            if lang == 'mix':
                spk_id = int(st.slider('选择一个说话人的ID，音频质量不一致（有的说话人音频质量较高）', -174, 174, 174))
            elif lang == 'zh':
                spk_id = int(st.slider('选择一个说话人的ID，音频质量不一致（有的说话人音频质量较高）', -174, 173, 0))
            elif lang == 'en':
                spk_id = 174
        with tab3:
            male = True
            text = st.text_input("输入需要语音合成的文本", value = "你好，我是数字人分身，很搞笑认识大家！")
        st.markdown("<hr />",unsafe_allow_html=True)
        st.button("开始合成音频", on_click = generate_on_wav)
        label = st.empty()

        if st.session_state.generate_on_wav:
            label.warning('音频合成中，请耐心等待！')
            paddlespeech_tts(text, voc, spk_id, lang)
            
            st.session_state.generate_on_wav = False
            st.session_state.generate_audio = True
            label.success('音频合成成功！！！')
            
        if os.path.exists(save_audio):
            st.audio(save_audio)
            with open(save_audio,'rb') as file:
                st.download_button(
                    label="Download Audio",
                    data=file,
                    file_name=save_audio,
                )
                
    elif choice == 'Audio': 
        audio = st.file_uploader("输入音频", type=['wav', 'mp3'])
        if audio:
            st.audio(audio)
            save_audio = audio.name
            with open(save_audio, 'wb') as f:
                f.write(audio.read())
            st.session_state.generate_audio = True
st.markdown("<hr />",unsafe_allow_html=True)


st.button("PaddleAvator生成", on_click = generate_on_video)
label = st.empty()
if st.session_state.generate_on_video:
    if not st.session_state.generate_face or not st.session_state.generate_audio:
        label.warning("请上传图片/视频 和语音 后再尝试", icon="⚠️")
        st.session_state.generate_on_video = False
    else:
        label.warning('正在生成，请耐心等待！！！')
        wav2lip(save_face, save_audio)
        if not os.path.exists('result.mp4'):
            label.warning('生成失败！！！请查看报错后再次生成')
        else:
            st.video('result.mp4')
            st.session_state.generate_on_video = False
            label.success('生成成功！！！')
            if os.path.exists(save_audio):
                os.system(f'rm {save_audio}')
            if os.path.exists(save_face):
                os.system(f'rm {save_face}')
