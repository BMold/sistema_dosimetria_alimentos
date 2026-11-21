import React from 'react';
import { useSimulationStore } from '../../store/useSimulationStore';
import { Card } from '../ui/Card';
import { ShieldCheck, Zap, ShieldAlert, AlertTriangle } from 'lucide-react';
import { useTranslation } from '../../hooks/useTranslation';

export const DosimetryIndicators: React.FC = () => {
  const { simulationData } = useSimulationStore();
  const { t, tPurpose } = useTranslation();

  if (!simulationData) return null;

  const { simulacion_dosimetria_radiacion, calculo_dosis_emision_3d_limite, clasificacion_alimento } = simulationData;
  const ind = simulacion_dosimetria_radiacion.indicadores_dosimetria_fisico_biologica;

  const showSafety = !!calculo_dosis_emision_3d_limite;
  const seguridad = calculo_dosis_emision_3d_limite?.indicadores_seguridad;
  const isAlertActive = seguridad?.alerta_limite_legal_excedido;
  const productoName = clasificacion_alimento?.tipo_item_detectado || 'papa';

  return (
    <Card className="p-4 h-full flex flex-col justify-between space-y-4">
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border-dim/50 pb-2">
          <div className="flex items-center space-x-2">
            <ShieldCheck className="h-4 w-4 text-nuclear" />
            <h3 className="font-heading font-bold text-sm text-white uppercase tracking-wider">
              {t('ind_title')}
            </h3>
          </div>
          <span className="text-[10px] font-mono text-nuclear-bright tracking-wider bg-nuclear-container/20 border border-nuclear-dark/50 px-2 py-0.5 rounded animate-pulse">
            {t('ind_badge')}
          </span>
        </div>

        {/* Physics Specs Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
          <div className="space-y-1 bg-surface-elevated/45 p-2 rounded border border-border-dim/50">
            <span className="text-[9px] font-mono text-text-muted uppercase block">{t('ind_energy')}</span>
            <span className="text-base font-mono font-bold text-text-primary">
              {ind.energia_depositada_total_Joules.toFixed(2)}
              <span className="text-xs font-sans text-text-secondary ml-1">J</span>
            </span>
          </div>

          <div className="space-y-1 bg-surface-elevated/45 p-2 rounded border border-border-dim/50">
            <span className="text-[9px] font-mono text-text-muted uppercase block">{t('ind_coef')}</span>
            <span className="text-base font-mono font-bold text-text-primary">
              {ind.coeficiente_atenuacion_lineal_mu.toFixed(4)}
              <span className="text-xs font-sans text-text-secondary ml-1">cm⁻¹</span>
            </span>
          </div>

          <div className="space-y-1 bg-surface-elevated/45 p-2 rounded border border-border-dim/50">
            <span className="text-[9px] font-mono text-text-muted uppercase block">{t('ind_uniformity')}</span>
            <span className="text-base font-mono font-bold text-text-primary font-heading">
              {ind.uniformidad_dosis_ratio_Dmax_Dmin.toFixed(2)}
            </span>
          </div>

          <div className="space-y-1 bg-surface-elevated/45 p-2 rounded border border-border-dim/50">
            <span className="text-[9px] font-mono text-text-muted uppercase block">{t('ind_density')}</span>
            <span className="text-base font-mono font-bold text-text-primary">
              {ind.densidad_masa_estimada_g_cm3.toFixed(3)}
              <span className="text-xs font-sans text-text-secondary ml-1">g/cm³</span>
            </span>
          </div>

          <div className="space-y-1 bg-surface-elevated/45 p-2 rounded border border-border-dim/50">
            <span className="text-[9px] font-mono text-text-muted uppercase block">{t('ind_ebr')}</span>
            <span className="text-base font-mono font-bold text-text-primary font-heading">
              {(ind.efectividad_biologica_relativa_EBR ?? 1.0).toFixed(1)}x
            </span>
          </div>

          <div className="space-y-1 bg-surface-elevated/45 p-2 rounded border border-border-dim/50">
            <span className="text-[9px] font-mono text-text-muted uppercase block">{t('ind_reduction')}</span>
            <span className="text-base font-mono font-bold text-nuclear-bright text-glow-green">
              -{ind.reduccion_logaritmica_carga_bacteriana.toFixed(1)} log₁₀
            </span>
          </div>
        </div>

        {/* Dosimetry Recommendation Summary */}
        <div className="bg-nuclear-container/10 border border-nuclear-dark/30 rounded p-3 mt-2 flex items-center space-x-3">
          <div className="p-1.5 rounded bg-nuclear-container/30 text-nuclear-bright">
            <Zap className="h-5 w-5" />
          </div>
          <div>
            <div className="text-[9px] font-mono text-text-secondary uppercase">
              {t('ind_rec_summary')} {tPurpose(simulacion_dosimetria_radiacion.proposito_fitosanitario_asignado)}
            </div>
            <div className="text-sm font-bold font-mono text-white">
              {simulacion_dosimetria_radiacion.dosis_superficie_objetivo_kGy.toFixed(2)} kGy (Kilogray)
            </div>
          </div>
        </div>

        {/* ==========================================================
            NUEVO: PANEL DE SEGURIDAD LEGAL Y MAPEO VIRTUAL DE CAPAS
            ========================================================== */}
        {showSafety && (
          <div className="border-t border-border-dim/40 pt-4 space-y-4 animate-fade-in">
            {/* Safety Title */}
            <div className="flex items-center space-x-2">
              <ShieldAlert className="h-4 w-4 text-cyan-rad" />
              <h4 className="font-heading font-bold text-xs text-white uppercase tracking-wider">
                {t('ind_safety_title')}
              </h4>
            </div>

            {/* Safety Specs Subgrid */}
            <div className="grid grid-cols-2 gap-3 bg-surface-elevated/20 p-3 rounded border border-border-dim/30">
              <div className="space-y-0.5">
                <span className="text-[8px] font-mono text-text-muted uppercase block">{t('ind_safety_dur')}</span>
                <span className="text-xs font-mono font-bold text-white">
                  {seguridad.DUR_calculado.toFixed(2)}
                </span>
              </div>
              <div className="space-y-0.5">
                <span className="text-[8px] font-mono text-text-muted uppercase block">{t('ind_safety_limit')}</span>
                <span className="text-xs font-mono font-bold text-white">
                  {seguridad.limite_legal_aplicado_kGy.toFixed(2)} kGy
                </span>
              </div>
              <div className="space-y-0.5">
                <span className="text-[8px] font-mono text-text-muted uppercase block">{t('ind_safety_core_real')}</span>
                <span className="text-xs font-mono font-bold text-cyan-rad text-glow-cyan">
                  {((calculo_dosis_emision_3d_limite.dosis_real_nucleo_kGy)).toFixed(3)} kGy
                </span>
              </div>
              <div className="space-y-0.5">
                <span className="text-[8px] font-mono text-text-muted uppercase block">{t('ind_safety_mass')}</span>
                <span className="text-xs font-mono font-bold text-white">
                  {calculo_dosis_emision_3d_limite.masa_calculada_kg.toFixed(4)} kg
                </span>
              </div>
            </div>

            {/* Virtual Layer Map */}
            <div className="bg-surface-void/40 border border-border-dim/40 rounded-lg p-3 space-y-2">
              <span className="text-[9px] font-mono font-bold text-text-secondary uppercase block tracking-wider">
                {t('ind_safety_layers')} ({calculo_dosis_emision_3d_limite.profundidad_penetrada_cm.toFixed(2)} cm)
              </span>
              <div className="space-y-2.5">
                {calculo_dosis_emision_3d_limite.mapeo_dosis_virtual.map((capa, idx) => {
                  const maxDose = Math.max(...calculo_dosis_emision_3d_limite.mapeo_dosis_virtual.map(c => c.dosis_kGy)) || 1.0;
                  const pct = Math.min((capa.dosis_kGy / maxDose) * 100, 100);
                  
                  return (
                    <div key={idx} className="space-y-1">
                      <div className="flex justify-between items-center text-[9px] font-mono">
                        <span className="text-white/80 font-medium">
                          {capa.capa} ({capa.profundidad_cm.toFixed(2)} cm)
                        </span>
                        <span className="text-cyan-rad font-bold">
                          {capa.dosis_kGy.toFixed(3)} kGy
                        </span>
                      </div>
                      <div className="h-1.5 w-full bg-black/60 rounded-full overflow-hidden border border-border-dim/30">
                        <div
                          className="h-full bg-gradient-to-r from-cyan-dark to-cyan-rad rounded-full transition-all duration-1000 ease-out"
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="mt-4 pt-3 border-t border-border-dim/50 text-[10px] font-mono text-text-muted flex items-center justify-between">
        <span>{t('ind_footer_source')}</span>
        <span>{t('ind_footer_std')}</span>
      </div>
    </Card>
  );
};
