import { motion, useReducedMotion } from 'framer-motion';
import { cn } from '@/lib/cn';

/**
 * Logo animé « un cacao en orbite ».
 * Une fève de cacao stylisée sur une orbite elliptique parcourue par un petit satellite,
 * avec une traînée lumineuse. Respecte `prefers-reduced-motion`.
 */
export function OrbitCacao({
  size = 220,
  className,
  spin = true,
}: {
  size?: number;
  className?: string;
  spin?: boolean;
}) {
  const reduce = useReducedMotion();
  const animate = spin && !reduce;

  return (
    <div
      className={cn('relative select-none', className)}
      style={{ width: size, height: size }}
      aria-hidden
    >
      <svg viewBox="0 0 200 200" width={size} height={size} className="overflow-visible">
        <defs>
          <linearGradient id="oc-pod" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor="#FF9A3C" />
            <stop offset="0.55" stopColor="#FF7A00" />
            <stop offset="1" stopColor="#7B3F00" />
          </linearGradient>
          <linearGradient id="oc-orbit" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0" stopColor="#00A651" stopOpacity="0.15" />
            <stop offset="0.5" stopColor="#00A651" stopOpacity="0.9" />
            <stop offset="1" stopColor="#00A651" stopOpacity="0.15" />
          </linearGradient>
          <radialGradient id="oc-glow" cx="0.5" cy="0.5" r="0.5">
            <stop offset="0" stopColor="#FF7A00" stopOpacity="0.55" />
            <stop offset="1" stopColor="#FF7A00" stopOpacity="0" />
          </radialGradient>
          <filter id="oc-blur" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="2.4" />
          </filter>
        </defs>

        {/* halo */}
        <circle cx="100" cy="100" r="78" fill="url(#oc-glow)" />

        {/* orbite */}
        <g transform="rotate(-22 100 100)">
          <ellipse
            cx="100"
            cy="100"
            rx="82"
            ry="34"
            fill="none"
            stroke="url(#oc-orbit)"
            strokeWidth="2"
          />
          {/* satellite + traînée */}
          <motion.g
            style={{ originX: '100px', originY: '100px' }}
            animate={animate ? { rotate: 360 } : undefined}
            transition={{ duration: 9, ease: 'linear', repeat: Infinity }}
          >
            <path
              d="M18 100a82 34 0 0 1 40 -29"
              fill="none"
              stroke="#FFFFFF"
              strokeOpacity="0.5"
              strokeWidth="3"
              strokeLinecap="round"
              filter="url(#oc-blur)"
            />
            <circle cx="18" cy="100" r="4.5" fill="#FFFFFF" />
            <circle cx="18" cy="100" r="9" fill="#FFFFFF" opacity="0.18" />
          </motion.g>
        </g>

        {/* fève de cacao */}
        <motion.g
          style={{ originX: '100px', originY: '100px' }}
          animate={animate ? { y: [0, -6, 0], rotate: [-4, 4, -4] } : undefined}
          transition={{ duration: 6, ease: 'easeInOut', repeat: Infinity }}
        >
          <path
            d="M100 52c20 10 30 34 22 58-4 12-13 24-22 30-9-6-18-18-22-30-8-24 2-48 22-58z"
            fill="url(#oc-pod)"
          />
          <path
            d="M100 58v78"
            stroke="#F4EAD5"
            strokeOpacity="0.85"
            strokeWidth="2.4"
            strokeLinecap="round"
          />
          {[68, 82, 96, 110, 124].map((y) => (
            <path
              key={y}
              d={`M100 ${y}q-10 5 -14 0M100 ${y}q10 5 14 0`}
              stroke="#F4EAD5"
              strokeOpacity="0.5"
              strokeWidth="1.6"
              fill="none"
            />
          ))}
        </motion.g>
      </svg>
    </div>
  );
}
