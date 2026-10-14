interface VoiceRecognitionAlternative {
  transcript: string;
}

interface VoiceRecognitionResult extends ArrayLike<VoiceRecognitionAlternative> {
  isFinal: boolean;
}

interface VoiceRecognitionResultList extends ArrayLike<VoiceRecognitionResult> {}

interface VoiceRecognitionEvent extends Event {
  results: VoiceRecognitionResultList;
}

type VoiceRecognitionError =
  | 'aborted'
  | 'audio-capture'
  | 'bad-grammar'
  | 'language-not-supported'
  | 'network'
  | 'no-speech'
  | 'not-allowed'
  | 'service-not-allowed';

interface VoiceRecognitionErrorEvent extends Event {
  error: VoiceRecognitionError;
}

interface VoiceRecognition {
  lang: string;
  interimResults: boolean;
  onresult: ((event: VoiceRecognitionEvent) => void) | null;
  onerror: ((event: VoiceRecognitionErrorEvent) => void) | null;
  onend: (() => void) | null;
  start: () => void;
  stop: () => void;
  abort: () => void;
}

interface VoiceRecognitionConstructor {
  new (): VoiceRecognition;
}

interface Window {
  SpeechRecognition?: VoiceRecognitionConstructor;
  webkitSpeechRecognition?: VoiceRecognitionConstructor;
}
