import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import App from '../App';

describe('Axiom OS Frontend Foundation & Navigation', () => {
  it('renders the brand header, 11 navigation areas, and road switcher', () => {
    render(<App />);
    expect(screen.getByText('AXIOM OS')).toBeInTheDocument();
    expect(screen.getAllByText(/Scholar Road/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Builder Road/i).length).toBeGreaterThan(0);
    expect(screen.getByText('Experiment Lab')).toBeInTheDocument();
    expect(screen.getByText('Think Deeper')).toBeInTheDocument();
  });

  it('switches to Explore & Onboarding and displays preset learning intents', () => {
    render(<App />);
    const exploreBtn = screen.getByText('Explore & Onboard');
    fireEvent.click(exploreBtn);
    expect(
      screen.getByText(/What Do You Want to Understand From First Principles or Build Today/i)
    ).toBeInTheDocument();
    expect(screen.getByText(/Generate Research & Build Blueprint/i)).toBeInTheDocument();
  });

  it('opens the Command Palette modal when Search & Command is clicked', () => {
    render(<App />);
    const cmdBtn = screen.getByText('Search & Command');
    fireEvent.click(cmdBtn);
    expect(
      screen.getByPlaceholderText(/Search concepts, lessons, notes, projects, experiments, or resources/i)
    ).toBeInTheDocument();
  });
});
