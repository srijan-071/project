import { NavLink, useLocation } from 'react-router-dom';
import { 
  Terminal, BarChart3, Layers, GitCompare, 
  Cpu, Box, Clock, FileText, Home, Menu, X 
} from 'lucide-react';
import { useState } from 'react';

const navItems = [
  { path: '/', label: 'HOME', icon: Home, num: '00' },
  { path: '/intelligence', label: 'INTELLIGENCE', icon: Terminal, num: '01' },
  { path: '/market-pulse', label: 'MARKET PULSE', icon: BarChart3, num: '02' },
  { path: '/batch', label: 'BATCH ANALYSIS', icon: Layers, num: '03' },
  { path: '/compare', label: 'COMPARISON', icon: GitCompare, num: '04' },
  { path: '/model-lab', label: 'MODEL LAB', icon: Cpu, num: '05' },
  { path: '/architecture', label: 'ARCHITECTURE', icon: Box, num: '06' },
  { path: '/history', label: 'HISTORY', icon: Clock, num: '07' },
  { path: '/docs', label: 'DOCUMENTATION', icon: FileText, num: '08' },
];

export default function Sidebar() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();

  return (
    <>
      {/* Mobile toggle */}
      <button 
        className="fixed top-3 left-3 z-[60] btn btn-ghost lg:hidden"
        onClick={() => setMobileOpen(!mobileOpen)}
      >
        {mobileOpen ? <X size={18} /> : <Menu size={18} />}
      </button>

      {/* Overlay */}
      {mobileOpen && (
        <div 
          className="fixed inset-0 bg-black/60 z-[45] lg:hidden"
          onClick={() => setMobileOpen(false)} 
        />
      )}

      <aside className={`app-sidebar ${mobileOpen ? 'open' : ''}`}>
        {/* Brand */}
        <div style={{ padding: '20px 20px 16px' }}>
          <div style={{ 
            fontFamily: 'var(--font-mono)', 
            fontSize: '0.75rem', 
            fontWeight: 700,
            letterSpacing: '0.15em',
            color: 'var(--accent-primary)',
            marginBottom: 4 
          }}>
            FIN<span style={{ color: 'var(--text-muted)' }}>//</span>SIGHT
          </div>
          <div style={{ 
            fontFamily: 'var(--font-mono)', 
            fontSize: '0.55rem',
            letterSpacing: '0.1em',
            color: 'var(--text-dim)' 
          }}>
            FINANCIAL INTELLIGENCE v1.0
          </div>
        </div>

        <div style={{ 
          height: 1, 
          background: 'var(--border-color)', 
          margin: '0 16px 12px' 
        }} />

        {/* Navigation */}
        <nav style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 2 }}>
          {navItems.map(item => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setMobileOpen(false)}
            >
              <span className="nav-num">{item.num}</span>
              <item.icon size={14} />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        {/* Model Status */}
        <div style={{ 
          padding: '16px 20px', 
          borderTop: '1px solid var(--border-color)',
          marginTop: 'auto' 
        }}>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            marginBottom: 8 
          }}>
            <span className="label-terminal">MODEL</span>
            <span style={{ 
              fontFamily: 'var(--font-mono)', 
              fontSize: '0.65rem',
              color: 'var(--text-secondary)' 
            }}>
              FinSight-TX v1.0
            </span>
          </div>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center' 
          }}>
            <span className="label-terminal">STATUS</span>
            <span style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: 6,
              fontFamily: 'var(--font-mono)', 
              fontSize: '0.65rem',
              color: 'var(--accent-primary)' 
            }}>
              <span className="status-dot status-dot-online" />
              ONLINE
            </span>
          </div>
        </div>
      </aside>
    </>
  );
}
