from video_decode import decode_video

decode_video(
    video_path="stego_video.mkv",
    password=11,       # SAME PASSWORD USED DURING ENCODE
    out_dir="recovered"    # recovered file will be saved here
)
    
    