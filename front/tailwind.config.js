/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	darkMode: 'class',
	theme: {
		extend: {
			animation: {
				// Existing animations
				drawLine: 'drawLine 2s ease-out forwards',
				expandWidth: 'expandWidth 1s ease-out forwards',

				// Enhanced UI/UX animations
				fadeInUp: 'fadeInUp 0.4s ease-out forwards',
				fadeInDown: 'fadeInDown 0.4s ease-out forwards',
				fadeInLeft: 'fadeInLeft 0.4s ease-out forwards',
				fadeInRight: 'fadeInRight 0.4s ease-out forwards',
				slideInUp: 'slideInUp 0.3s ease-out forwards',
				slideInDown: 'slideInDown 0.3s ease-out forwards',
				scaleIn: 'scaleIn 0.3s ease-out forwards',
				scaleInBounce: 'scaleInBounce 0.5s ease-out forwards',

				// Card animations
				cardReveal: 'cardReveal 0.4s ease-out forwards',
				cardHover: 'cardHover 0.3s ease-out forwards',
				cardPress: 'cardPress 0.1s ease-out forwards',

				// Loading and skeleton animations
				shimmer: 'shimmer 1.5s ease-in-out infinite',
				'pulse-soft': 'pulse-soft 2s ease-in-out infinite',
				skeleton: 'skeleton 1.2s ease-in-out infinite',

				// Interactive animations
				ripple: 'ripple 0.6s ease-out forwards',
				'bounce-soft': 'bounce-soft 0.5s ease-out forwards',
				wiggle: 'wiggle 0.5s ease-in-out forwards',
				'rubber-band': 'rubber-band 0.8s ease-out forwards',

				// Progress animations
				'progress-fill': 'progress-fill 1s ease-out forwards',
				'count-up': 'count-up 1.5s ease-out forwards',
				'rotate-180': 'rotate-180 0.3s ease-out forwards',
				'rotate-360': 'rotate-360 0.5s ease-out forwards',

				// Page transitions
				'page-enter': 'page-enter 0.3s ease-out forwards',
				'page-exit': 'page-exit 0.2s ease-in forwards',
				'modal-enter': 'modal-enter 0.3s ease-out forwards',
				'modal-exit': 'modal-exit 0.2s ease-in forwards',

				// Notification animations
				'toast-enter': 'toast-enter 0.3s ease-out forwards',
				'toast-exit': 'toast-exit 0.3s ease-in forwards',
				'notification-slide': 'notification-slide 0.4s ease-out forwards'
			},
			keyframes: {
				// Existing keyframes
				drawLine: {
					to: {
						'stroke-dashoffset': '0',
						opacity: '1'
					}
				},
				expandWidth: {
					to: {
						width: '100%'
					}
				},

				// Enhanced fade animations
				fadeInUp: {
					'0%': {
						opacity: '0',
						transform: 'translateY(30px)'
					},
					'100%': {
						opacity: '1',
						transform: 'translateY(0)'
					}
				},
				fadeInDown: {
					'0%': {
						opacity: '0',
						transform: 'translateY(-30px)'
					},
					'100%': {
						opacity: '1',
						transform: 'translateY(0)'
					}
				},
				fadeInLeft: {
					'0%': {
						opacity: '0',
						transform: 'translateX(-30px)'
					},
					'100%': {
						opacity: '1',
						transform: 'translateX(0)'
					}
				},
				fadeInRight: {
					'0%': {
						opacity: '0',
						transform: 'translateX(30px)'
					},
					'100%': {
						opacity: '1',
						transform: 'translateX(0)'
					}
				},

				// Slide animations
				slideInUp: {
					'0%': {
						transform: 'translateY(100%)',
						opacity: '0'
					},
					'100%': {
						transform: 'translateY(0)',
						opacity: '1'
					}
				},
				slideInDown: {
					'0%': {
						transform: 'translateY(-100%)',
						opacity: '0'
					},
					'100%': {
						transform: 'translateY(0)',
						opacity: '1'
					}
				},

				// Scale animations
				scaleIn: {
					'0%': {
						opacity: '0',
						transform: 'scale(0.8)'
					},
					'100%': {
						opacity: '1',
						transform: 'scale(1)'
					}
				},
				scaleInBounce: {
					'0%': {
						opacity: '0',
						transform: 'scale(0.3)'
					},
					'50%': {
						opacity: '1',
						transform: 'scale(1.05)'
					},
					'70%': {
						transform: 'scale(0.98)'
					},
					'100%': {
						opacity: '1',
						transform: 'scale(1)'
					}
				},

				// Card specific animations
				cardReveal: {
					'0%': {
						opacity: '0',
						transform: 'translateY(30px) scale(0.95)'
					},
					'100%': {
						opacity: '1',
						transform: 'translateY(0) scale(1)'
					}
				},
				cardHover: {
					'0%': {
						transform: 'translateY(0) scale(1)',
						boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
					},
					'100%': {
						transform: 'translateY(-4px) scale(1.02)',
						boxShadow: '0 20px 40px rgba(0,0,0,0.15)'
					}
				},
				cardPress: {
					'0%': {
						transform: 'scale(1)'
					},
					'50%': {
						transform: 'scale(0.98)'
					},
					'100%': {
						transform: 'scale(1)'
					}
				},

				// Loading animations
				shimmer: {
					'0%': {
						backgroundPosition: '-200% 0'
					},
					'100%': {
						backgroundPosition: '200% 0'
					}
				},
				'pulse-soft': {
					'0%, 100%': {
						opacity: '1'
					},
					'50%': {
						opacity: '0.7'
					}
				},
				skeleton: {
					'0%': {
						backgroundColor: 'rgb(243 244 246)'
					},
					'50%': {
						backgroundColor: 'rgb(229 231 235)'
					},
					'100%': {
						backgroundColor: 'rgb(243 244 246)'
					}
				},

				// Interactive animations
				ripple: {
					'0%': {
						transform: 'scale(0)',
						opacity: '0.6'
					},
					'100%': {
						transform: 'scale(4)',
						opacity: '0'
					}
				},
				'bounce-soft': {
					'0%, 20%, 53%, 80%, 100%': {
						transform: 'translate3d(0,0,0)'
					},
					'40%, 43%': {
						transform: 'translate3d(0, -8px, 0)'
					},
					'70%': {
						transform: 'translate3d(0, -4px, 0)'
					},
					'90%': {
						transform: 'translate3d(0, -2px, 0)'
					}
				},
				wiggle: {
					'0%, 7%': {
						transform: 'rotateZ(0)'
					},
					'15%': {
						transform: 'rotateZ(-3deg)'
					},
					'20%': {
						transform: 'rotateZ(2deg)'
					},
					'25%': {
						transform: 'rotateZ(-2deg)'
					},
					'30%': {
						transform: 'rotateZ(1deg)'
					},
					'35%': {
						transform: 'rotateZ(-1deg)'
					},
					'40%, 100%': {
						transform: 'rotateZ(0)'
					}
				},
				'rubber-band': {
					'0%': {
						transform: 'scale(1)'
					},
					'30%': {
						transform: 'scaleX(1.25) scaleY(0.75)'
					},
					'40%': {
						transform: 'scaleX(0.75) scaleY(1.25)'
					},
					'50%': {
						transform: 'scaleX(1.15) scaleY(0.85)'
					},
					'65%': {
						transform: 'scaleX(0.95) scaleY(1.05)'
					},
					'75%': {
						transform: 'scaleX(1.05) scaleY(0.95)'
					},
					'100%': {
						transform: 'scale(1)'
					}
				},

				// Progress animations
				'progress-fill': {
					'0%': {
						width: '0%'
					},
					'100%': {
						width: 'var(--progress-width, 100%)'
					}
				},
				'count-up': {
					'0%': {
						transform: 'translateY(20px)',
						opacity: '0'
					},
					'100%': {
						transform: 'translateY(0)',
						opacity: '1'
					}
				},
				'rotate-180': {
					'0%': {
						transform: 'rotate(0deg)'
					},
					'100%': {
						transform: 'rotate(180deg)'
					}
				},
				'rotate-360': {
					'0%': {
						transform: 'rotate(0deg)'
					},
					'100%': {
						transform: 'rotate(360deg)'
					}
				},

				// Page transitions
				'page-enter': {
					'0%': {
						opacity: '0',
						transform: 'translateY(20px)'
					},
					'100%': {
						opacity: '1',
						transform: 'translateY(0)'
					}
				},
				'page-exit': {
					'0%': {
						opacity: '1',
						transform: 'translateY(0)'
					},
					'100%': {
						opacity: '0',
						transform: 'translateY(-20px)'
					}
				},
				'modal-enter': {
					'0%': {
						opacity: '0',
						transform: 'scale(0.9) translateY(20px)'
					},
					'100%': {
						opacity: '1',
						transform: 'scale(1) translateY(0)'
					}
				},
				'modal-exit': {
					'0%': {
						opacity: '1',
						transform: 'scale(1) translateY(0)'
					},
					'100%': {
						opacity: '0',
						transform: 'scale(0.9) translateY(20px)'
					}
				},

				// Notification animations
				'toast-enter': {
					'0%': {
						opacity: '0',
						transform: 'translateX(100%)'
					},
					'100%': {
						opacity: '1',
						transform: 'translateX(0)'
					}
				},
				'toast-exit': {
					'0%': {
						opacity: '1',
						transform: 'translateX(0)'
					},
					'100%': {
						opacity: '0',
						transform: 'translateX(100%)'
					}
				},
				'notification-slide': {
					'0%': {
						opacity: '0',
						transform: 'translateY(-100%)'
					},
					'100%': {
						opacity: '1',
						transform: 'translateY(0)'
					}
				}
			},

			// Enhanced spacing scale
			spacing: {
				18: '4.5rem',
				88: '22rem',
				112: '28rem',
				128: '32rem'
			},

			// Enhanced typography
			fontSize: {
				xs: ['0.75rem', { lineHeight: '1rem' }],
				sm: ['0.875rem', { lineHeight: '1.25rem' }],
				base: ['1rem', { lineHeight: '1.5rem' }],
				lg: ['1.125rem', { lineHeight: '1.75rem' }],
				xl: ['1.25rem', { lineHeight: '1.75rem' }],
				'2xl': ['1.5rem', { lineHeight: '2rem' }],
				'3xl': ['1.875rem', { lineHeight: '2.25rem' }],
				'4xl': ['2.25rem', { lineHeight: '2.5rem' }],
				'5xl': ['3rem', { lineHeight: '1' }],
				'6xl': ['3.75rem', { lineHeight: '1' }],
				'7xl': ['4.5rem', { lineHeight: '1' }],
				'8xl': ['6rem', { lineHeight: '1' }],
				'9xl': ['8rem', { lineHeight: '1' }]
			},

			// Enhanced shadows
			boxShadow: {
				soft: '0 2px 4px rgba(0,0,0,0.05)',
				medium: '0 4px 12px rgba(0,0,0,0.1)',
				large: '0 8px 24px rgba(0,0,0,0.15)',
				xl: '0 12px 32px rgba(0,0,0,0.2)',
				'2xl': '0 16px 48px rgba(0,0,0,0.25)',
				'inner-soft': 'inset 0 2px 4px rgba(0,0,0,0.05)',
				glow: '0 0 20px rgba(59, 130, 246, 0.3)',
				'glow-green': '0 0 20px rgba(34, 197, 94, 0.3)',
				'glow-red': '0 0 20px rgba(239, 68, 68, 0.3)'
			},

			// Enhanced border radius
			borderRadius: {
				xl: '0.75rem',
				'2xl': '1rem',
				'3xl': '1.5rem',
				'4xl': '2rem'
			},

			// Backdrop blur utilities
			backdropBlur: {
				xs: '2px',
				sm: '4px',
				md: '8px',
				lg: '12px',
				xl: '16px',
				'2xl': '24px',
				'3xl': '40px'
			},

			// Enhanced color palette
			colors: {
				// Brand colors
				brand: {
					50: '#eff6ff',
					100: '#dbeafe',
					200: '#bfdbfe',
					300: '#93c5fd',
					400: '#60a5fa',
					500: '#3b82f6',
					600: '#2563eb',
					700: '#1d4ed8',
					800: '#1e40af',
					900: '#1e3a8a'
				},

				// Success colors
				success: {
					50: '#f0fdf4',
					100: '#dcfce7',
					200: '#bbf7d0',
					300: '#86efac',
					400: '#4ade80',
					500: '#22c55e',
					600: '#16a34a',
					700: '#15803d',
					800: '#166534',
					900: '#14532d'
				},

				// Warning colors
				warning: {
					50: '#fffbeb',
					100: '#fef3c7',
					200: '#fde68a',
					300: '#fcd34d',
					400: '#fbbf24',
					500: '#f59e0b',
					600: '#d97706',
					700: '#b45309',
					800: '#92400e',
					900: '#78350f'
				},

				// Error colors
				error: {
					50: '#fef2f2',
					100: '#fee2e2',
					200: '#fecaca',
					300: '#fca5a5',
					400: '#f87171',
					500: '#ef4444',
					600: '#dc2626',
					700: '#b91c1c',
					800: '#991b1b',
					900: '#7f1d1d'
				}
			},

			// Enhanced transitions
			transitionTimingFunction: {
				'bounce-in': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
				smooth: 'cubic-bezier(0.4, 0, 0.2, 1)',
				'smooth-in': 'cubic-bezier(0.4, 0, 1, 1)',
				'smooth-out': 'cubic-bezier(0, 0, 0.2, 1)'
			},

			// Enhanced z-index scale
			zIndex: {
				60: '60',
				70: '70',
				80: '80',
				90: '90',
				100: '100'
			}
		}
	},
	plugins: [require('@tailwindcss/forms'), require('@tailwindcss/typography')]
};
