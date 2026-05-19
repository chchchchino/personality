import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { PersonalityApiService } from './services/personality-api.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
})
export class AppComponent {
  personality = '';
  userWords = '';
  resultText = '';
  errorText = '';
  loading = false;

  constructor(private readonly api: PersonalityApiService) {}

  onSubmit(): void {
    const personality = this.personality.trim();
    const words = this.userWords.trim();

    if (!personality || !words) {
      this.errorText = 'Please enter a personality and some text to translate.';
      this.resultText = '';
      return;
    }

    this.loading = true;
    this.errorText = '';
    this.resultText = '';

    this.api.translate(personality, words).subscribe({
      next: (res) => {
        this.loading = false;
        if (res.success && res.translated_words) {
          this.resultText = res.translated_words;
        } else {
          this.errorText = res.error ?? 'Translation failed.';
        }
      },
      error: (err) => {
        this.loading = false;
        const detail = err?.error?.detail;
        this.errorText =
          typeof detail === 'string'
            ? detail
            : 'Could not reach the personality server. Is it running on port 8000?';
      },
    });
  }
}
