<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<?fileVersion 4.0.0?><cproject storage_type_id="org.eclipse.cdt.core.XmlProjectDescriptionStorage">
	<storageModule moduleId="org.eclipse.cdt.core.settings">
		<cconfiguration id="0.910961921">
			<storageModule buildSystemId="org.eclipse.cdt.managedbuilder.core.configurationDataProvider" id="0.910961921" moduleId="org.eclipse.cdt.core.settings" name="Default">
				<externalSettings/>
				<extensions>
					<extension id="org.eclipse.cdt.core.VCErrorParser" point="org.eclipse.cdt.core.ErrorParser"/>
					<extension id="org.eclipse.cdt.core.GmakeErrorParser" point="org.eclipse.cdt.core.ErrorParser"/>
					<extension id="org.eclipse.cdt.core.CWDLocator" point="org.eclipse.cdt.core.ErrorParser"/>
					<extension id="org.eclipse.cdt.core.GCCErrorParser" point="org.eclipse.cdt.core.ErrorParser"/>
					<extension id="org.eclipse.cdt.core.GASErrorParser" point="org.eclipse.cdt.core.ErrorParser"/>
					<extension id="org.eclipse.cdt.core.GLDErrorParser" point="org.eclipse.cdt.core.ErrorParser"/>
					<extension id="org.eclipse.cdt.core.ELF" point="org.eclipse.cdt.core.BinaryParser"/>
				</extensions>
			</storageModule>
			<storageModule moduleId="cdtBuildSystem" version="4.0.0">
				<configuration artifactName="{{project_name}}" buildProperties="" description="" id="0.910961921" name="Default" parent="org.eclipse.cdt.build.core.prefbase.cfg">
					<folderInfo id="0.910961921." name="/" resourcePath="">
						<toolChain id="org.eclipse.cdt.build.core.prefbase.toolchain.952979152" name="No ToolChain" resourceTypeBasedDiscovery="false" superClass="org.eclipse.cdt.build.core.prefbase.toolchain">
							<targetPlatform binaryParser="org.eclipse.cdt.core.ELF" id="org.eclipse.cdt.build.core.prefbase.toolchain.952979152.52310970" name=""/>
							<builder cleanBuildTarget="-f -c eclipse run --target clean" command="platformio" id="org.eclipse.cdt.build.core.settings.default.builder.1519453406" incrementalBuildTarget="-f -c eclipse run" keepEnvironmentInBuildfile="false" managedBuildOn="false" name="Gnu Make Builder" superClass="org.eclipse.cdt.build.core.settings.default.builder"/>
							<tool id="org.eclipse.cdt.build.core.settings.holder.libs.1409095472" name="holder for library settings" superClass="org.eclipse.cdt.build.core.settings.holder.libs"/>
							<tool id="org.eclipse.cdt.build.core.settings.holder.1624502120" name="Assembly" superClass="org.eclipse.cdt.build.core.settings.holder">
								<option id="org.eclipse.cdt.build.core.settings.holder.incpaths.239157887" name="Include Paths" superClass="org.eclipse.cdt.build.core.settings.holder.incpaths" valueType="includePath">
									% for include in includes:
									% if "toolchain" in include:
									% continue
									% end
                                    % if include.startswith(user_home_dir):
                                    % if "windows" in systype:
									<listOptionValue builtIn="false" value="${USERPROFILE}{{include.replace(user_home_dir, '')}}"/>
									% else:
									<listOptionValue builtIn="false" value="${HOME}{{include.replace(user_home_dir, '')}}"/>
									% end
                                    % else:
									<listOptionValue builtIn="false" value="{{include}}"/>
									% end
									% end
								</option>
								<option id="org.eclipse.cdt.build.core.settings.holder.symbols.922107295" name="Symbols" superClass="org.eclipse.cdt.build.core.settings.holder.symbols" valueType="definedSymbols">
									% for define in defines:
									<listOptionValue builtIn="false" value="{{define}}"/>
									% end
								</option>
								<inputType id="org.eclipse.cdt.build.core.settings.holder.inType.149990277" languageId="org.eclipse.cdt.core.assembly" languageName="Assembly" sourceContentType="org.eclipse.cdt.core.asmSource" superClass="org.eclipse.cdt.build.core.settings.holder.inType"/>
							</tool>
							<tool id="org.eclipse.cdt.build.core.settings.holder.54121539" name="GNU C++" superClass="org.eclipse.cdt.build.core.settings.holder">
								<option id="org.eclipse.cdt.build.core.settings.holder.incpaths.1096940598" name="Include Paths" superClass="org.eclipse.cdt.build.core.settings.holder.incpaths" valueType="includePath">
									% for include in includes:
									% if "toolchain" in include:
									% continue
									% end
                                    % if include.startswith(user_home_dir):
                                    % if "windows" in systype:
									<listOptionValue builtIn="false" value="${USERPROFILE}{{include.replace(user_home_dir, '')}}"/>
									% else:
									<listOptionValue builtIn="false" value="${HOME}{{include.replace(user_home_dir, '')}}"/>
                                    % end
                                    % else:
									<listOptionValue builtIn="false" value="{{include}}"/>
									% end
									% end
								</option>
								<option id="org.eclipse.cdt.build.core.settings.holder.symbols.1198905600" name="Symbols" superClass="org.eclipse.cdt.build.core.settings.holder.symbols" valueType="definedSymbols">
									% for define in defines:
									<listOptionValue builtIn="false" value="{{define}}"/>
									% end
								</option>
								<inputType id="org.eclipse.cdt.build.core.settings.holder.inType.762536863" languageId="org.eclipse.cdt.core.g++" languageName="GNU C++" sourceContentType="org.eclipse.cdt.core.cxxSource,org.eclipse.cdt.core.cxxHeader" superClass="org.eclipse.cdt.build.core.settings.holder.inType"/>
							</tool>
							<tool id="org.eclipse.cdt.build.core.settings.holder.1310559623" name="GNU C" superClass="org.eclipse.cdt.build.core.settings.holder">
								<option id="org.eclipse.cdt.build.core.settings.holder.incpaths.41298875" name="Include Paths" superClass="org.eclipse.cdt.build.core.settings.holder.incpaths" valueType="includePath">
									% for include in includes:
									% if "toolchain" in include:
									% continue
									% end
                                    % if include.startswith(user_home_dir):
                                    % if "windows" in systype:
									<listOptionValue builtIn="false" value="${USERPROFILE}{{include.replace(user_home_dir, '')}}"/>
									% else:
									<listOptionValue builtIn="false" value="${HOME}{{include.replace(user_home_dir, '')}}"/>
                                    % end
                                    % else:
									<listOptionValue builtIn="false" value="{{include}}"/>
									% end
									% end
								</option>
								<option id="org.eclipse.cdt.build.core.settings.holder.symbols.884639970" name="Symbols" superClass="org.eclipse.cdt.build.core.settings.holder.symbols" valueType="definedSymbols">
									% for define in defines:
									<listOptionValue builtIn="false" value="{{define}}"/>
									% end
								</option>
								<inputType id="org.eclipse.cdt.build.core.settings.holder.inType.549319812" languageId="org.eclipse.cdt.core.gcc" languageName="GNU C" sourceContentType="org.eclipse.cdt.core.cSource,org.eclipse.cdt.core.cHeader" superClass="org.eclipse.cdt.build.core.settings.holder.inType"/>
							</tool>
						</toolChain>
					</folderInfo>
				</configuration>
			</storageModule>
			<storageModule moduleId="org.eclipse.cdt.core.externalSettings"/>
		</cconfiguration>
	</storageModule>
	<storageModule moduleId="cdtBuildSystem" version="4.0.0">
		<project id="{{project_name}}.null.189551033" name="{{project_name}}"/>
	</storageModule>
	<storageModule moduleId="scannerConfiguration">
		<autodiscovery enabled="true" problemReportingEnabled="true" selectedProfileId=""/>
		<scannerConfigBuildInfo instanceId="0.910961921">
			<autodiscovery enabled="true" problemReportingEnabled="true" selectedProfileId=""/>
		</scannerConfigBuildInfo>
	</storageModule>
	<storageModule moduleId="org.eclipse.cdt.core.LanguageSettingsProviders"/>
	<storageModule moduleId="refreshScope" versionNumber="2">
		<configuration configurationName="Default">
			<resource resourceType="PROJECT" workspacePath="/{{env_name}}"/>
		</configuration>
	</storageModule>
	<storageModule moduleId="org.eclipse.cdt.internal.ui.text.commentOwnerProjectMappings"/>
</cproject>
