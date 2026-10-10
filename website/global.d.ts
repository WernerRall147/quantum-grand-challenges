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

interface VoiceRecognitionErrorEvent extends Event {
  error: string;
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
