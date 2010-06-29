audio_encoders = {
                  'Vorbis' :
                   {
                    'plugin' : 'vorbisenc'
                   }
                 }
video_encoders = {
                  'VP8' :
                   {
                    'plugin' : 'vp8enc'
                   },
                  'Theora' :
                   {
                    'plugin' : 'theoraenc'
                   },
                  'Dirac' :
                   {
                    'plugin' : 'schroenc'
                   }
                  }
muxers = {
          'Matroska' :
           {
            'plugin' : 'matroskamux',
            'extension' : 'mkv'
           }
          }
