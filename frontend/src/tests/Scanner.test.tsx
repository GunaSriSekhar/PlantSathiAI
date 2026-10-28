import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { Scanner } from '../pages/Scanner';

describe('Scanner Component', () => {
  it('renders scanner title and action buttons', () => {
    render(
      <BrowserRouter>
        <Scanner />
      </BrowserRouter>
    );

    expect(screen.getByText(/Plant & Leaf Scanner/i)).toBeDefined();
    expect(screen.getByText(/Browse Files/i)).toBeDefined();
  });
});
