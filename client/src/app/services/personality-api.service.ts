import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

export interface TranslateRequest {
  personality: string;
  words: string;
}

export interface TranslateResponse {
  success: boolean;
  translated_words: string | null;
  error: string | null;
}

@Injectable({ providedIn: 'root' })
export class PersonalityApiService {
  private readonly baseUrl = '/api';

  constructor(private readonly http: HttpClient) {}

  translate(personality: string, words: string): Observable<TranslateResponse> {
    return this.http.post<TranslateResponse>(`${this.baseUrl}/translate`, {
      personality,
      words,
    });
  }
}
